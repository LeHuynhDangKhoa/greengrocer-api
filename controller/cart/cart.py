from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants

class CartController(BaseController):
    """
    Xử lý các chức năng liên quan đến giỏ hàng
    Attribute
        pgsql: chứa dữ liệu kết nối với cơ sở dữ liệu để thực hiện truy vấn
    """
    def __init__(self, pgsql: PGSQL):
        """
        Khởi tạo class 
        Input:
	        pgsql (class PGSQL): class dùng để truy vấn đến cơ sở dữ liệu PostgreSQL
        Output:
            None
        """
        self.pgsql = pgsql

    def CartBlueprint(self):
        """
        Tạo Blueprint dùng để đăng kí cho thư viện flask
        Input:
        Output:
            Blueprint
        """
        cart = Blueprint('cart', __name__)

        @cart.route('/cart/store', methods=['POST'])
        def CartStore():
            """
            Lưu trữ thông tin giỏ hàng
            Input:
            Output:
                Response
            """
            # Validate detail
            if "detail" not in request.json:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_CART])
            
            err = self.pgsql.CartStore(request.get_json())
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, "")

        return (cart)