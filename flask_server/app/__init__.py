from flask import Flask
import os
import json


def create_app():

        CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'config.json'))
        with open(CONFIG_PATH, "r") as f:
                config_data = json.load(f)

        app = Flask(__name__, template_folder="templates", static_folder="static")
        app.jinja_env.cache = {}
        app.config.update(config_data)

        from .routes import main
        app.register_blueprint(main, url_prefix= "/api")

        return app