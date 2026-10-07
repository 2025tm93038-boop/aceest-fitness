"""
ACEest Fitness & Gym - Flask Application
Version 1.1: Web UI with templates; JSON API under /api.
"""
import io
import os
from functools import wraps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
from fpdf import FPDF

import db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
db.init_db()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.verify_user(username, password)
        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(request.args.get("next") or url_for("clients"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

PROGRAMS = {
    "Fat Loss": {
        "workout": "Mon: 5x5 Back Squat + AMRAP | Tue: EMOM 20min Assault Bike | "
                    "Wed: Bench Press + 21-15-9 | Thu: 10RFT Deadlifts/Box Jumps | Fri: Active Recovery",
        "diet": "B: 3 Egg Whites + Oats | L: Grilled Chicken + Brown Rice | D: Fish Curry + Millet Roti | "
                "Target: 2000 kcal",
    },
    "Muscle Gain": {
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | Thu: Front Squat 4x8 | "
                    "Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats | L: Chicken Biryani | D: Mutton Curry + Jeera Rice | Target: 3200 kcal",
    },
    "Beginner": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups. Focus: Technique Mastery.",
        "diet": "Balanced meals: Idli-Sambar, Rice-Dal, Chapati. Protein: 120g/day",
    },
}


@app.route("/")
def home():
    return render_template("index.html", programs=list(PROGRAMS.keys()), plan=None, selected=None)


@app.route("/plan")
def plan():
    selected = request.args.get("program", "")
    program = PROGRAMS.get(selected)
    return render_template(
        "index.html",
        programs=list(PROGRAMS.keys()),
        plan=program,
        selected=selected if program else None,
    )


@app.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        program = request.form.get("program", "")
        if not name or program not in PROGRAMS:
            return jsonify({"error": "name and a valid program are required"}), 400
        db.add_client(name, program)
    return render_template("clients.html", clients=db.list_clients(), programs=list(PROGRAMS.keys()))


@app.route("/clients/<name>")
@login_required
def client_detail(name):
    client = db.get_client(name)
    if client is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    plan = PROGRAMS.get(client["program"], {})
    return render_template(
        "client_detail.html",
        client=client,
        plan=plan,
        workouts=db.list_workouts(name),
        progress=db.list_progress(name),
    )


@app.route("/clients/<name>/workouts", methods=["POST"])
@login_required
def add_workout(name):
    if db.get_client(name) is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    date = request.form.get("date", "")
    workout_type = request.form.get("workout_type", "")
    duration = request.form.get("duration_min", "0")
    notes = request.form.get("notes", "")
    if not date or not workout_type or not duration.isdigit():
        return jsonify({"error": "date, workout_type and numeric duration_min are required"}), 400
    db.add_workout(name, date, workout_type, int(duration), notes)
    return client_detail(name)


@app.route("/clients/<name>/progress", methods=["POST"])
@login_required
def add_progress(name):
    if db.get_client(name) is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    week = request.form.get("week", "")
    adherence = request.form.get("adherence", "")
    if not week or not adherence.isdigit():
        return jsonify({"error": "week and numeric adherence are required"}), 400
    try:
        db.add_progress(name, week, int(adherence))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return client_detail(name)


@app.route("/clients/<name>/report.pdf")
@login_required
def client_report(name):
    client = db.get_client(name)
    if client is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    plan = PROGRAMS.get(client["program"], {})

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"ACEest Client Report - {client['name']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0, 8,
        f"Program: {client['program']}\n\nWorkout Plan:\n{plan.get('workout', '')}\n\n"
        f"Diet Plan:\n{plan.get('diet', '')}",
    )

    buffer = io.BytesIO(pdf.output())
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{client['name']}_report.pdf",
    )


@app.route("/clients/<name>/chart.png")
@login_required
def client_chart(name):
    if db.get_client(name) is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    progress = db.list_progress(name)

    fig, ax = plt.subplots(figsize=(6, 3))
    if progress:
        weeks = [p["week"] for p in progress]
        adherence = [p["adherence"] for p in progress]
        ax.plot(weeks, adherence, marker="o")
    ax.set_title(f"{name} - Weekly Adherence")
    ax.set_ylabel("%")
    ax.set_ylim(0, 100)
    ax.grid(True)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@app.route("/api/clients")
def api_list_clients():
    return jsonify(db.list_clients())


@app.route("/api/programs")
def api_list_programs():
    return jsonify(list(PROGRAMS.keys()))


@app.route("/api/programs/<program_name>")
def api_get_program(program_name):
    program = PROGRAMS.get(program_name)
    if program is None:
        return jsonify({"error": f"Program '{program_name}' not found"}), 404
    return jsonify({"program": program_name, **program})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
