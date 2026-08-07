import os
import sys
import paramiko

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ask or specify target VPS credentials
HOST = input("Enter Linux VPS IP address: ").strip() if len(sys.argv) < 2 else sys.argv[1]
USER = input("Enter VPS SSH username (default: root): ").strip() or "root"
PASS = input("Enter VPS SSH password: ").strip()

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = "/var/www/tgalarm"

print(f"\n[+] Connecting to VPS SSH {USER}@{HOST}...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, port=22, username=USER, password=PASS, timeout=30)
    print("[+] SSH Connection Successful!")
except Exception as e:
    print(f"[-] Connection failed: {e}")
    sys.exit(1)

def run_cmd(cmd, ignore_error=False):
    print(f"[>] Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out)
    if err and not ignore_error:
        print(f"[!] Stderr: {err}")
    return out

print("\n[+] Installing Python 3 & PM2 on VPS...")
run_cmd("apt-get update -y && apt-get install -y python3 python3-pip python3-venv curl")
run_cmd("curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs")
run_cmd("npm install -g pm2")

print(f"\n[+] Creating remote directory {REMOTE_DIR}...")
run_cmd(f"mkdir -p {REMOTE_DIR}")

print("\n[+] Uploading project files via SFTP...")
sftp = ssh.open_sftp()

files_to_upload = [
    "monitor.py",
    "admin_bot.py",
    "alerter.py",
    "config.py",
    "state_manager.py",
    "requirements.txt",
    "ecosystem.config.js",
    ".env",
    "monitor_session.session",
    "caller_session.session",
    "state.json",
    "README.md"
]

for fname in files_to_upload:
    local_path = os.path.join(LOCAL_DIR, fname)
    remote_path = f"{REMOTE_DIR}/{fname}"
    if os.path.exists(local_path):
        print(f"  Uploading {fname} -> {remote_path}")
        sftp.put(local_path, remote_path)
    else:
        print(f"  [!] Skipping {fname} (not found locally)")

sftp.close()

print("\n[+] Installing Python dependencies on VPS...")
run_cmd(f"cd {REMOTE_DIR} && pip3 install -r requirements.txt")

print("\n[+] Starting services under PM2...")
run_cmd(f"cd {REMOTE_DIR} && pm2 reload ecosystem.config.js || pm2 start ecosystem.config.js")
run_cmd("pm2 save")

print("\n[+] Deployment completed successfully!")
print("[+] Status:")
run_cmd("pm2 status")

ssh.close()
