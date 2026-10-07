"""
ACEest Fitness & Gym - Flask Application
Version 1.1: Web UI with templates; JSON API under /api.
"""
from flask import Flask, jsonify, render_template, request

import db

app = Flask(__name__)
db.init_db()

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
def clients():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        program = request.form.get("program", "")
        if not name or program not in PROGRAMS:
            return jsonify({"error": "name and a valid program are required"}), 400
        db.add_client(name, program)
    return render_template("clients.html", clients=db.list_clients(), programs=list(PROGRAMS.keys()))


@app.route("/clients/<name>")
def client_detail(name):
    client = db.get_client(name)
    if client is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    plan = PROGRAMS.get(client["program"], {})
    return render_template("client_detail.html", client=client, plan=plan)


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
