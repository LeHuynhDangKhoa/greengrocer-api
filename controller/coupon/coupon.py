from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from datetime import datetime

class CouponController(BaseController):
    """
    Xử lý các chức năng liên quan đến mã giảm giá
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

    def CouponBlueprint(self):
        """
        Tạo Blueprint dùng để đăng kí cho thư viện flask
        Input:
        Output:
            Blueprint
        """
        coupon = Blueprint('coupon', __name__)

        @coupon.route('/coupon/<code>', methods=['GET'])
        def CouponGet(code):
            """
            Lấy thông tin mã giảm giá
            Input:
                code (string): mã giảm giá
            Output:
                Response
            """
            # Get coupon
            coupon, err = self.pgsql.GetCouponByCode(code)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

            if coupon == None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_COUPON_NOT_FOUND])

            # Validate coupon
            if datetime.now().timestamp() < datetime.strptime(str(coupon["valid_from"]), '%Y-%m-%d %H:%M:%S%z').timestamp() or datetime.now().timestamp() > datetime.strptime(str(coupon["valid_to"]), '%Y-%m-%d %H:%M:%S%z').timestamp():
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_COUPON])

            # Handle successfull response
            coupon["valid_from"] = str(coupon["valid_from"])
            coupon["valid_to"] = str(coupon["valid_to"])
            return self.handleResponse(HTTPStatus.OK.value, coupon)

        return (coupon)