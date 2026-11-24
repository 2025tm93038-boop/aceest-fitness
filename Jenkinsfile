pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    // Poll GitHub every 2 minutes and build when new commits appear
    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        VENV_DIR      = '.venv'
        // EDIT: your Docker Hub username
        DOCKER_USER   = 'divyag07'
        IMAGE_NAME    = "${DOCKER_USER}/aceest-fitness"
        // Jenkins credential ID (Manage Jenkins > Credentials): Docker Hub username + access token
        DOCKER_CREDS  = 'dockerhub-creds'
        // Name of the SonarQube server and scanner tool configured in Jenkins
        SONAR_SERVER  = 'sonar'
        SCANNER_HOME  = tool 'sonar-scanner'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // Version = nearest git tag (e.g. v3.3.0) or short commit hash
                    env.APP_VERSION = sh(
                        script: 'git describe --tags --always',
                        returnStdout: true
                    ).trim().replaceFirst('^v', '')
                    echo "Building application version ${env.APP_VERSION}"
                }
            }
        }

        stage('Set up environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Unit Tests + Coverage') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v --cov=. --cov-report=xml --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONAR_SERVER}") {
                    sh '${SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectVersion=${APP_VERSION}'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                // Needs a SonarQube webhook pointing to <jenkins-url>/sonarqube-webhook/
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('BUILD: Docker Image') {
            steps {
                sh '''
                    docker build --build-arg APP_VERSION=${APP_VERSION} \
                        -t ${IMAGE_NAME}:${APP_VERSION} \
                        -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Test inside container') {
            steps {
                sh '''
                    docker run --rm --user root \
                        -v "$(pwd)/tests:/app/tests" \
                        -v "$(pwd)/pytest.ini:/app/pytest.ini" \
                        --entrypoint sh ${IMAGE_NAME}:${APP_VERSION} \
                        -c "pip install --no-cache-dir pytest && pytest -v"
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDS}",
                                                  usernameVariable: 'HUB_USER',
                                                  passwordVariable: 'HUB_TOKEN')]) {
                    sh '''
                        echo "${HUB_TOKEN}" | docker login -u "${HUB_USER}" --password-stdin
                        docker push ${IMAGE_NAME}:${APP_VERSION}
                        docker push ${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            // Runs only once the k8s manifests exist in the repo (added in the next phase)
            when { expression { fileExists('k8s/rolling-update/deployment.yaml') } }
            steps {
                sh '''
                    sed "s|DOCKERHUB_USER|${DOCKER_USER}|g" k8s/rolling-update/deployment.yaml | kubectl apply -f -
                    kubectl apply -f k8s/rolling-update/service.yaml
                    kubectl set image deployment/aceest-fitness \
                        aceest-fitness=${IMAGE_NAME}:${APP_VERSION}
                    if ! kubectl rollout status deployment/aceest-fitness --timeout=120s; then
                        echo "Rollout failed - rolling back to the last stable version"
                        kubectl rollout undo deployment/aceest-fitness
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml, reports/*.xml', allowEmptyArchive: true
        }
        success {
            echo "Build ${env.BUILD_NUMBER} succeeded - version ${env.APP_VERSION}"
        }
        failure {
            echo 'Pipeline failed - check the stage logs above.'
        }
        cleanup {
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}
