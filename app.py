from flask import Flask
from database import pgsql
from flask_cors import CORS
from controller.product.product import ProductController

def create_app():
    app = Flask(__name__, static_folder='images')
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # setup with the configuration provided
    app.config.from_object('config.DevelopmentConfig')

    # setup all our dependencies
    pg = pgsql.PGSQL(app.config)

    productCtrl = ProductController(pg)

    # # register blueprint
    app.register_blueprint(productCtrl.ProductBlueprint())

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
