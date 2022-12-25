from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from flask_cors import CORS, cross_origin

class ProductController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def ProductBlueprint(self):
        product = Blueprint('product', __name__)

        @product.route('/products', methods=['GET'])
        def ProductList():           
            # Validate category_id > 0
            categoryId = request.args.get("category")
            # if categoryId:
            #     try:
            #         categoryId = int(categoryId)
            #         if categoryId <= 0:
            #             raise ValueError(Message[Constants.MSG_INVALID_CATEGORY_ID])
            #     except ValueError as e:
            #         return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CATEGORY_ID])

            # Validate star > 0
            star = request.args.get("star")
            if star:
                try:
                    star = int(star)
                    if star <= 0:
                        raise ValueError(Message[Constants.MSG_INVALID_STAR])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_STAR])

            # Validate discount = true or false
            discount = request.args.get("discount")
            if discount:
                if discount == "true":
                    discount = 1
                elif discount == "false":
                    discount = 0
                else:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_DISCOUNT])

            # Validate price_from > 0
            priceFrom = request.args.get("price_from")
            if priceFrom:
                try:
                    priceFrom = float(priceFrom)
                    if priceFrom < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE_FROM])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE_FROM])

            # Validate price_from > 0
            priceTo = request.args.get("price_to")
            if priceTo:
                try:
                    priceTo = float(priceTo)
                    if priceTo < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE_TO])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE_TO])

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

        @product.route('/categories', methods=['GET'])
        def CategoryList():
            res, err = self.pgsql.CategoryList()
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            else:
                return self.handleResponse(HTTPStatus.OK.value, res)

        @product.route('/products/<id>', methods=['GET'])
        def ProductView(id):
            try:
                id = int(id)
                res, err = self.pgsql.GetProductById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                else:
                    if res != None:
                        return self.handleResponse(HTTPStatus.OK.value, res)
                    else:
                        return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_PRODUCT_NOT_FOUND])
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_ID])

        return (product)
