from flask import Flask
from database import pgsql
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from controller.product.product import ProductController
from controller.auth.auth import AuthController

def create_app():
    app = Flask(__name__, static_folder='images')
    CORS(app)
    bcrypt = Bcrypt(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # setup with the configuration provided
    app.config.from_object('config.DevelopmentConfig')

    # setup all our dependencies
    pg = pgsql.PGSQL(app.config)

    # register blueprint
    productCtrl = ProductController(pg)
    app.register_blueprint(productCtrl.ProductBlueprint())
    authCtrl = AuthController(pg)
    app.register_blueprint(authCtrl.AuthBlueprint(app.config['UPLOAD_AVATAR'], bcrypt))

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
