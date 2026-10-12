# ACEest Fitness & Gym

Flask web app for gym management: view fitness programs (Fat Loss, Muscle Gain, Beginner), and, after admin login, manage clients, log workouts and weekly adherence, and generate PDF reports and charts. Built for a DevOps assignment (Git, Pytest, Docker, GitHub Actions, Jenkins).

## Local setup
Requires Python 3.9+.

```bash
git clone https://github.com/2025tm93038-boop/aceest-fitness.git
cd aceest-fitness
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                 # runs on http://localhost:5000
```

Admin login: `admin` / `admin123` (at `/login`).

## Run with Docker
```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```

## Run tests manually
```bash
pip install pytest
pytest -v
```
18 tests cover the programs API, login, client management, workout and progress validation, and the PDF/chart endpoints.

## CI/CD overview

**GitHub Actions** (`.github/workflows/main.yml`) runs on every push and pull request:
1. **Build, Lint & Test**: installs dependencies, lints with flake8, runs Pytest.
2. **Docker Build & Test**: builds the Docker image and runs the Pytest suite inside the container.

**Jenkins** (`Jenkinsfile`) is a second, independent BUILD gate. It pulls the latest code from GitHub and runs: Checkout, Environment setup, Lint, Unit Tests, Docker image build.

Together, GitHub Actions gives fast feedback on every commit, and Jenkins re-validates the same code in a separate controlled build environment.
