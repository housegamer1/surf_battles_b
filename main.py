from flask import Flask
import src.backend as backend
import threading
from src.api import api_routes

app = Flask(__name__)
app.register_blueprint(api_routes)

def main():
    #start main backend loop in a thread
    loop = threading.Thread(target=backend.backend_loop)
    loop.start()

    #start flask handling in main thread
    app.run()
    print("Shutting down")
    backend.threadcontrol.set() #close thread once flask closes
    loop.join()
    

if __name__ == "__main__":
    main()
