from flask import Flask, render_template
import subprocess

app = Flask(__name__)

# Monitor Read target — the Ubuntu "clinical data" VM, accessed read-only as Mread
MREAD_HOST = "192.168.64.2"   # swap to the real class network IP when on the shared switch
MREAD_USER = "Mread"
SSH_KEY = "/home/darrel/.ssh/mread_key"
SUBNET = "192.168.64.0/24"    # swap to 10.0.0.0/24 on the real class network

SSH_BASE = [
    "ssh", "-i", SSH_KEY,
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=5",
    f"{MREAD_USER}@{MREAD_HOST}",
]


def run_remote(cmd, timeout=15):
    """Run a command on the Ubuntu target over SSH as Mread, return combined output."""
    full_cmd = SSH_BASE + cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        out = result.stdout
        if result.stderr:
            out += "\n--- stderr ---\n" + result.stderr
        return out
    except subprocess.TimeoutExpired:
        return "Command timed out."


def run_remote_follow(cmd, follow_seconds=4):
    """Run a following command (like tail -f) remotely, capturing output for a short window."""
    full_cmd = SSH_BASE + cmd
    proc = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = proc.communicate(timeout=follow_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    if err:
        out += "\n--- stderr ---\n" + err
    return out


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/users")
def users():
    # Who is logged into the Ubuntu target right now
    return run_remote(["w"])


@app.route("/ssh")
def ssh():
    # Recent login history on the Ubuntu target
    return run_remote(["wtmpdb", "last", "-n", "20"])


@app.route("/failed")
def failed():
    # Live auth.log tail on the target, filtered to failed password attempts
    raw = run_remote_follow(["sudo", "tail", "-f", "/var/log/auth.log"])
    failed_lines = [line for line in raw.splitlines() if "Failed password" in line]
    if not failed_lines:
        return "No failed login attempts seen in this window."
    return "\n".join(failed_lines)


@app.route("/network")
def network():
    # Real nmap sweep of the class subnet, run from Kali (the admin workstation)
    try:
        return subprocess.check_output(
            ["nmap", "-sV", "-T4", "--max-retries", "1", SUBNET],
            text=True,
            timeout=120,
        )
    except subprocess.CalledProcessError as e:
        return f"nmap exited with an error:\n{e.output}"
    except subprocess.TimeoutExpired:
        return "nmap scan timed out."


@app.route("/patients")
def patients():
    # Real read-only check of the clinical data directory on the target
    return run_remote(["ls", "-la", "/srv/clinical-data"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
