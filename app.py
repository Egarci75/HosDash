from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/users")
def users():
    return subprocess.check_output("w", shell=True, text=True)

@app.route("/ssh")
def ssh():
    return subprocess.check_output("last | head -20", shell=True, text=True)

@app.route("/failed")
def failed():
    try:
        return subprocess.check_output(
            "grep 'Failed password' /var/log/auth.log | tail -20",
            shell=True,
            text=True
        )
    except:
        return "No failed login entries found."

@app.route("/network")
def network():
    return subprocess.check_output(
        "ip addr",
        shell=True,
        text=True
    )

@app.route("/patients")
def patients():
    return """
Patient Monitoring

Patient data source not configured yet.
Waiting for integration.
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
