import subprocess
import threading

def run_flask():
    subprocess.run(["python", "app.py"], cwd="backend", check=True)

def run_react():
    subprocess.run(["npm", "start"], cwd="frontend", check=True)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_flask)
    t2 = threading.Thread(target=run_react)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
