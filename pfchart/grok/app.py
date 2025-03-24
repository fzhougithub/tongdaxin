from flask import Flask, render_template, request, send_from_directory
import subprocess
import os
import shutil

app = Flask(__name__)

# Paths
SCRIPT_DIR = "/var/tellme/work/tongdaxin/pfchart/grok"
CHART_OUTPUT_DIR = "/mnt/c/Users/Admin/Pictures/stock"
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
PYTHON_EXECUTABLE = "/var/tellme/work/p3/bin/python3"  # Path to virtual environment's Python

# Ensure the static directory exists
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route("/", methods=["GET", "POST"])
def index():
    chart_url = None
    error = None

    if request.method == "POST":
        # Get user inputs
        symbol = request.form.get("symbol")
        step = request.form.get("step")

        # Validate inputs
        if not symbol or not step:
            error = "Please provide both a stock symbol and a step size."
        else:
            try:
                step = float(step)  # Ensure step is a float
                if step <= 0:
                    raise ValueError("Step size must be positive.")

                # Generate the chart by calling the script
                chart_filename = f"pf_chart_{symbol}_step_{step:.2f}.jpg"
                chart_path = os.path.join(CHART_OUTPUT_DIR, chart_filename)
                static_chart_path = os.path.join(STATIC_DIR, chart_filename)

                # Run the script using the virtual environment's Python
                cmd = [PYTHON_EXECUTABLE, "pfbucket_psql_function.py", symbol, "--step", str(step)]
                result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True)

                # Check if the chart was generated
                if not os.path.exists(chart_path):
                    error = f"Failed to generate chart. Script output: {result.stdout}\n{result.stderr}"
                else:
                    # Copy the chart to the static directory for web access
                    shutil.copy(chart_path, static_chart_path)
                    chart_url = f"/static/{chart_filename}"

            except ValueError as e:
                error = f"Invalid step size: {str(e)}"
            except Exception as e:
                error = f"An error occurred: {str(e)}"

    return render_template("index.html", chart_url=chart_url, error=error)

@app.route("/static/<filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
