from flask import Flask
from database import pgsql

# blueprint import
from controller.product.product import ProductController
# from apps.app2.views import app2

def create_app():
    app = Flask(__name__, static_folder='images')
    # setup with the configuration provided
    app.config.from_object('config.DevelopmentConfig')

    # setup all our dependencies
    pg = pgsql.PGSQL(app.config)

    productCtrl = ProductController(pg)

    # # register blueprint
    app.register_blueprint(productCtrl.ProductBlueprint())

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=3000)
