import subprocess

app = Flask(name)

@app.route("/")
def home():
    return """
    <h1>Hospital Monitoring Dashboard</h1>

    <form action="/users">
        <button type="submit">Logged-In Users</button>
    </form>

    <form action="/ssh">
        <button type="submit">SSH Activity</button>
    </form>

    <form action="/failed">
        <button type="submit">Failed Logins</button>
    </form>

    <form action="/network">
        <button type="submit">Network Status</button>
    </form>

    <form action="/patients">
        <button type="submit">Patient Data</button>
    </form>
    """

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

if name == "main":
    app.run(host="0.0.0.0", port=5000)
