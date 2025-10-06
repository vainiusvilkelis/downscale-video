from flask import Flask
from routes.drive_transfer import drive_bp

app = Flask(__name__)
app.register_blueprint(drive_bp)

@app.route("/")
def healthcheck():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
