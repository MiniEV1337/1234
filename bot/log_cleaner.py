import os, time
TTL = 10 * 86400
for f in os.listdir("logs"):
    path = os.path.join("logs", f)
    if os.path.isfile(path) and time.time() - os.path.getmtime(path) > TTL:
        os.remove(path)
        print(f"🧹 Удалено: {path}")
