pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(false)
    }

    environment {
        VENV_DIR = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls the latest code from the configured GitHub repo/branch
                checkout scm
            }
        }

        stage('Set up environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8 pytest
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

        stage('Unit Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest -v --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('BUILD: Docker Image') {
            steps {
                // Secondary validation layer: confirm the app packages and
                // installs cleanly in a controlled, containerized environment.
                sh 'docker build -t aceest-fitness:${BUILD_NUMBER} .'
            }
        }
    }

    post {
        success {
            echo 'Jenkins BUILD stage completed successfully.'
        }
        failure {
            echo 'Jenkins BUILD stage failed - check the stage logs above.'
        }
        cleanup {
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}
