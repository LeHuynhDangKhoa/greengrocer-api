from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants

class CartController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def CartBlueprint(self):
        cart = Blueprint('cart', __name__)

        @cart.route('/cart/store', methods=['POST'])
        def CouponGet():
            # Validate detail
            if "detail" not in request.json:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_CART])
            
            err = self.pgsql.CartStore(request.get_json())
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, "")

        return (cart)