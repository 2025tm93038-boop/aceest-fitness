"""
ACEest Fitness & Gym - Flask Application
Version 1.0: Baseline program lookup (workout + diet chart per program).
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

# Data store for program specification (mirrors the original desktop v1.0 prototype)
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
    return jsonify({
        "message": "Welcome to ACEest Fitness & Gym API",
        "available_programs": list(PROGRAMS.keys()),
    })


@app.route("/programs")
def list_programs():
    return jsonify(list(PROGRAMS.keys()))


@app.route("/programs/<program_name>")
def get_program(program_name):
    program = PROGRAMS.get(program_name)
    if program is None:
        return jsonify({"error": f"Program '{program_name}' not found"}), 404
    return jsonify({"program": program_name, **program})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
