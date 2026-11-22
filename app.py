from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/users")
def users():
    output = subprocess.check_output("w", shell=True, text=True)
    return f"<pre>{output}</pre>"

@app.route("/ssh")
def ssh():
    return "<h1>SSH Activity</h1><p>Coming Soon</p>"

@app.route("/failed")
def failed():
    return "<h1>Failed Logins</h1><p>Coming Soon</p>"

@app.route("/network")
def network():
    return "<h1>Network Status</h1><p>Coming Soon</p>"

@app.route("/patients")
def patients():
    return "<h1>Patient Data</h1><p>Coming Soon</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
