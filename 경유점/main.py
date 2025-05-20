import threading
from web.app import run_flask
from web.dash_app import run_dash

def run_multithread(flask_func, dash_func):
    t1 = threading.Thread(target=flask_func)
    t2 = threading.Thread(target=dash_func)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

if __name__ == "__main__":
    run_multithread(run_flask, run_dash)