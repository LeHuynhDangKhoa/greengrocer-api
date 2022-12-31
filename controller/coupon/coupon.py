from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from datetime import datetime

class CouponController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def CouponBlueprint(self):
        coupon = Blueprint('coupon', __name__)

        @coupon.route('/coupon/<code>', methods=['GET'])
        def CouponGet(code):
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