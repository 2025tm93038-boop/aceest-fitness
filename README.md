# ACEest Fitness & Gym

A Flask web application for ACEest Fitness & Gym: members pick a fitness program (Fat Loss,
Muscle Gain, Beginner) to see its workout and diet plan, and admins can register clients, log
workouts, track weekly adherence, and generate PDF reports and adherence charts.

Built as part of a DevOps assignment demonstrating version control, automated testing,
containerization, and CI/CD with GitHub Actions and Jenkins.

## Features

- Public program lookup (`/`, `/plan`) and JSON API (`/api/programs`)
- Admin login (session-based) protecting client management
- SQLite-backed client records, workout logs, and weekly adherence tracking
- PDF client report generation (fpdf2) and adherence chart image (matplotlib)
- 18-test Pytest suite with isolated per-test databases
- Dockerized with a slim, non-root production image
- CI/CD via GitHub Actions; a Jenkinsfile for the Jenkins BUILD quality gate

## Project layout

```
app.py                     Flask application and routes
db.py                      SQLite persistence layer
templates/                 Jinja2 HTML templates
tests/                     Pytest suite (test client + fixtures)
Dockerfile, .dockerignore  Container image definition
.github/workflows/main.yml GitHub Actions CI/CD pipeline
Jenkinsfile                Jenkins BUILD pipeline definition
requirements.txt           Python dependencies
```

## Local setup and execution

Requires Python 3.12+.

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd aceest-fitness

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app starts on `http://localhost:5000`. A default admin account (`admin` / `admin123`) is
seeded automatically on first run for logging in at `/login` to manage clients — change the
password in `db.py` before deploying anywhere real, and set a real `SECRET_KEY` environment
variable instead of the development default in `app.py`.

### Running with Docker

```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```

## Running tests manually

```bash
pip install -r requirements.txt pytest
pytest -v
```

Each test gets its own temporary SQLite database via a `conftest.py` fixture, so tests don't
interfere with each other or with any local `aceest_fitness.db` file.

## CI/CD pipeline overview

### GitHub Actions (`.github/workflows/main.yml`)

Triggered on every `push` and `pull_request`, in two jobs:

1. **Build, Lint & Test** — installs dependencies, runs `flake8` (hard-fails on syntax
   errors/undefined names, soft-warns on style), then runs the full Pytest suite.
2. **Docker Image Build & Containerized Test** — builds the Docker image, then runs the Pytest
   suite *inside* that built container (test files are mounted in at test time rather than
   shipped in the production image — see `.dockerignore`) to confirm the containerized
   environment behaves the same as the host.

### Jenkins (`Jenkinsfile`)

Configured as a secondary, server-side quality gate that pulls the latest code from GitHub and
performs a clean build:

1. **Checkout** — pulls the latest commit from the configured GitHub repository/branch.
2. **Set up environment** — creates a fresh virtualenv and installs dependencies.
3. **Lint** — flake8 syntax/error check.
4. **Unit Tests** — runs Pytest and publishes JUnit XML results via the `junit` post-build step.
5. **BUILD: Docker Image** — builds the Docker image, confirming the app packages and installs
   cleanly in a controlled, isolated environment, independent of GitHub Actions.

**How the two fit together:** GitHub Actions is the fast, always-on gate that runs on every
push/PR directly on GitHub's infrastructure. Jenkins acts as an additional, independently
configured BUILD stage (e.g. on a self-hosted agent) that re-validates the same checkout,
dependency install, lint, test, and Docker build steps — so a change only reaches "ready to
ship" once it has passed both pipelines.

#### Setting up the Jenkins job

1. Install Jenkins and the **Pipeline**, **Git**, and **Docker Pipeline** plugins.
2. Ensure `python3`, `pip`, and `docker` are available on the Jenkins agent.
3. New Item → Pipeline → under *Pipeline*, choose "Pipeline script from SCM", set SCM to Git,
   point it at this repository's URL, and set the script path to `Jenkinsfile`.
4. Add a GitHub webhook (or poll SCM) so pushes trigger a build automatically.

## Notes / possible improvements

- Credentials are stored in plaintext in SQLite for simplicity; a production version should
  hash passwords (e.g. with `werkzeug.security.generate_password_hash`).
- `SECRET_KEY` and the default admin password should be supplied via environment variables /
  secrets in any real deployment, not left as source-code defaults.
