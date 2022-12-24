from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants

class ProductController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def ProductBlueprint(self):
        product = Blueprint('product', __name__)

        @product.route('/products', methods=['GET'])
        def ProductList():           
            # Validate category_id > 0
            categoryId = request.args.get("category_id")
            if categoryId:
                try:
                    categoryId = int(categoryId)
                    if categoryId <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_CATEGORY_ID])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CATEGORY_ID])
            else:
                categoryId = 0

            # Validate star > 0
            star = request.args.get("star")
            if star:
                try:
                    star = int(star)
                    if star <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_STAR])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_STAR])
            else:
                star = 0

            # Validate 0 <= discount <= 1
            discount = request.args.get("discount")
            if discount:
                try:
                    discount = float(discount)
                    if discount < 0 or discount > 1:
                        raise ValueError(Message[Constants.MSG_INVALID_DISCOUNT])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_DISCOUNT])
            else:
                discount = -1

            # Validate price_from > 0
            priceFrom = request.args.get("price_from")
            if priceFrom:
                try:
                    priceFrom = float(priceFrom)
                    if priceFrom <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE_FROM])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE_FROM])
            else:
                priceFrom = 0

            # Validate price_from > 0
            priceTo = request.args.get("price_to")
            if priceTo:
                try:
                    priceTo = float(priceTo)
                    if priceTo <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE_TO])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE_TO])
            else:
                priceTo = 0

            # Validate limit
            limit = request.args.get("limit")
            if limit:
                try:
                    limit = int(limit)
                    if limit <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_LIMIT])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_LIMIT])
            else:
                limit = 10

            # Validate offset
            offset = request.args.get("offset")
            if offset:
                try:
                    offset = int(offset)
                    if offset < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_LIMIT])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_OFFSET])
            else:
                offset = 0

            # Validate order is asc or desc
            order = request.args.get("order")
            if order:
                if order != "asc" and order != "desc":
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_ORDER])
            else:
                order = "desc"

            # Validate sortby
            sort = request.args.get("sort")
            if sort:
                if sort == "price":
                    sort = "discounted_price"
            else:
                sort = "id"

            # Validate search
            search = request.args.get("search")


            res, err = self.pgsql.ProductList(categoryId, star, discount, priceFrom, priceTo, search, order, sort, limit, offset)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            else:
                total = 0
                if len(res) > 0:
                    total = res[0]["total"]
                return self.handleResponseList(HTTPStatus.OK.value, limit, offset, total, res)

        return (product)
