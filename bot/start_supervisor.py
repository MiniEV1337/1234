import os
import subprocess

candidates = [
    "/app/supervisord.conf",
    "/app/bot/supervisord.conf",
    "/etc/supervisord.conf",
]

for path in candidates:
    if os.path.isfile(path):
        print(f"🟢 Found: {path}")
        subprocess.run(["supervisord", "-c", path])
        break
else:
    print("🔴 supervisord.conf not found in any known location.")
    exit(1)
