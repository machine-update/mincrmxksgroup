import os

from crm import create_app

app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=3000, debug=debug, use_reloader=debug)
