import os
from flask import Flask


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    from master_stego.routes import register_routes

    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

