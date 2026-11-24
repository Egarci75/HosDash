from flask import Flask, render_template, Response
import subprocess
import re

app = Flask(__name__)


def run_remote_follow(cmd, follow_seconds=4):
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
    return subprocess.getoutput("w")

@app.route("/ssh")
def ssh():
    return sub_process.getoutput("last -n 20")
@app.route("/failed")
def failed():
    return subprocess.getoutput(
        "grep 'Failed password' /var/log/auth.log | tail -20"
    )
@app.route("/network")
def network():
    try:
        raw = subprocess.check_output(
            ["nmap", "-sV", "-T4", "--max-retries", "1", "-oG", "-", SUBNET],
            text=True,
            timeout=150,
        )
    except subprocess.CalledProcessError as e:
        return f"nmap exited with an error:\n{e.output}"
    except subprocess.TimeoutExpired:
        return "nmap scan timed out."

    hosts = []
    for line in raw.splitlines():
        if not line.startswith("Host:"):
            continue
        ip_match = re.match(r"Host:\s+(\S+)", line)
        ip = ip_match.group(1) if ip_match else "unknown"

        if "Status: Up" in line:
            if not any(h["ip"] == ip for h in hosts):
                hosts.append({"ip": ip, "status": "Up", "ports": []})
        elif "Ports:" in line:
            ports_str = line.split("Ports:", 1)[1].split("Ignored State:")[0]
            port_entries = [p.strip() for p in ports_str.split(",") if p.strip()]
            parsed_ports = []
            for entry in port_entries:
                fields = entry.split("/")
                if len(fields) >= 5:
                    port, state, proto, _, service = fields[:5]
                    parsed_ports.append({
                        "port": port,
                        "proto": proto,
                        "state": state,
                        "service": service or "unknown",
                    })
            existing = next((h for h in hosts if h["ip"] == ip), None)
            if existing:
                existing["ports"] = parsed_ports
            else:
                hosts.append({"ip": ip, "status": "Up", "ports": parsed_ports})

    if not hosts:
        return "No live hosts found."

    rows = ""
    for h in hosts:
        if h["ports"]:
            port_list = "".join(
                f'<li><code>{p["port"]}/{p["proto"]}</code> &mdash; {p["service"]} '
                f'<span style="color:#4caf50">({p["state"]})</span></li>'
                for p in h["ports"]
            )
            ports_html = f'<ul style="margin:0;padding-left:1.2em">{port_list}</ul>'
        else:
            ports_html = "<em>no open ports found</em>"

        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #444;font-weight:bold;color:#9ad1ff">{h['ip']}</td>
            <td style="padding:8px;border-bottom:1px solid #444;color:#4caf50">{h['status']}</td>
            <td style="padding:8px;border-bottom:1px solid #444">{ports_html}</td>
        </tr>
        """

    table = f"""
    <table style="width:100%;border-collapse:collapse;font-family:monospace;color:#eee">
        <thead>
            <tr style="text-align:left;border-bottom:2px solid #666">
                <th style="padding:8px">Host</th>
                <th style="padding:8px">Status</th>
                <th style="padding:8px">Open Ports / Services</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    return Response(table, mimetype="text/html")

@app.route("/patients")
def patients():
    return subprocess.getoutput(
        "ls -la /srv/clinical-data"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
