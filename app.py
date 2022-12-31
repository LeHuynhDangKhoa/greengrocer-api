from flask import Flask
from database import pgsql
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from controller.product.product import ProductController
from controller.auth.auth import AuthController
from controller.user.user import UserController
from controller.category.category import CategoryController
from controller.coupon.coupon import CouponController
from controller.cart.cart import CartController

def create_app():
    app = Flask(__name__, static_folder='images')
    CORS(app)
    bcrypt = Bcrypt(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # setup with the configuration provided
    # app.config.from_object('config.DevelopmentConfig')
    app.config.from_object('config.ProductionConfig')

    # setup all our dependencies
    pg = pgsql.PGSQL(app.config)

    # register blueprint
    productCtrl = ProductController(pg)
    app.register_blueprint(productCtrl.ProductBlueprint(app.config['UPLOAD_PRODUCT']))
    authCtrl = AuthController(pg)
    app.register_blueprint(authCtrl.AuthBlueprint(app.config['UPLOAD_AVATAR'], bcrypt))
    userCtrl = UserController(pg)
    app.register_blueprint(userCtrl.UserBlueprint(app.config['UPLOAD_AVATAR']))
    categoryCtrl = CategoryController(pg)
    app.register_blueprint(categoryCtrl.CategoryBlueprint())
    couponCtrl = CouponController(pg)
    app.register_blueprint(couponCtrl.CouponBlueprint())
    cartCtrl = CartController(pg)
    app.register_blueprint(cartCtrl.CartBlueprint())

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
