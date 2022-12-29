from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime
import imghdr
import os

class ProductController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def ProductBlueprint(self, productPath):
        product = Blueprint('product', __name__)

        @product.route('/products', methods=['GET'])
        def ProductList():           
            # Validate category_id > 0
            categoryId = request.args.get("category")

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

            # Get product list
            res, err = self.pgsql.ProductList(categoryId, star, discount, priceFrom, priceTo, search, order, sort, limit, offset)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response 
            total = 0
            if len(res) > 0:
                total = res[0]["total"]
            return self.handleResponseList(HTTPStatus.OK.value, limit, offset, total, res)

        @product.route('/products/<id>', methods=['GET'])
        def ProductView(id):
            try:
                # Get product by id
                id = int(id)
                res, err = self.pgsql.GetProductById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if res == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_PRODUCT_NOT_FOUND])
                    
                # Handle successfull response
                return self.handleResponse(HTTPStatus.OK.value, res)
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_ID])

        @product.route('/products', methods=['POST'])
        def ProductAdd():
            values = []
            # Validate name
            if "name" in request.form:
                # Check name if existed
                res, err = self.pgsql.GetProductByName(request.form["name"])
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                if res != None:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_PRODUCT_NAME])
                values.append(request.form["name"])
            else:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_PRODUCT_NAME])

            # Validate price
            if "price" in request.form:
                try:
                    price = float(request.form["price"])
                    if price < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE])
                    values.append(price)
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE])
            else:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_PRICE])

            # Validate star
            star = 3
            if "star" in request.form:
                try:
                    star = int(request.form["star"])
                    if star < 0 or star > 5:
                        raise ValueError(Message[Constants.MSG_INVALID_STAR])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_STAR])
            values.append(star)

            # Validate description
            description = ""
            if "description" in request.form:
                description = request.form["description"]
            values.append(description)

            # Validate discount
            discount = 0
            if "discount" in request.form:
                try:
                    discount = float(request.form["discount"])
                    if discount < 0 or discount > 1:
                        raise ValueError(Message[Constants.MSG_INVALID_PRODUCT_DISCOUNT])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_DISCOUNT])
            values.append(discount)

            # Validate category
            categoryId = 0
            if "category_id" in request.form:
                try:
                    categoryId = int(request.form["category_id"])
                    if categoryId < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_CATEGORY_ID])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CATEGORY_ID])
            values.append(categoryId)

            # Validate image
            image = ""
            if "image" in request.files:
                file = request.files["image"]
                if file and imghdr.what(file) != None:
                    # Hash filename to MD5
                    hash = hashlib.md5()
                    hash.update((secure_filename(file.filename) + str(datetime.now())).encode())
                    filename = hash.hexdigest() + "." + secure_filename(file.filename).split(".")[len(secure_filename(file.filename).split(".")) - 1]

                    # Store file
                    image = productPath + filename
                    file.save(image)
                else:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_IMAGE])
            values.append(image)
                    
            # Inert new product
            err = self.pgsql.InsertNewProduct(values)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, "")

        @product.route('/products/<id>', methods=['PUT'])
        def ProductEdit(id):
            try:
                # Get product by id
                id = int(id)
                product, err = self.pgsql.GetProductById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if product == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_PRODUCT_NOT_FOUND])

                # Get updated field
                oldName = product["name"]
                oldAvatar = product["image"]
                for key, value in request.form.items():
                    if key in product and key != "id":
                        product[key] = value
                
                # Check username if name
                if oldName != product["name"]:
                    res, err = self.pgsql.GetProductByName(product["name"])
                    if err != None:
                        return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                    if res != None:
                        return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_PRODUCT_NAME])

                # Validate price
                try:
                    price = float(product["price"])
                    if price < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_PRICE])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRICE])

                # Validate star
                star = 3
                try:
                    star = int(product["star"])
                    if star < 0 or star > 5:
                        raise ValueError(Message[Constants.MSG_INVALID_STAR])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_STAR])

                # Validate discount
                try:
                    discount = float(product["discount"])
                    if discount < 0 or discount > 1:
                        raise ValueError(Message[Constants.MSG_INVALID_PRODUCT_DISCOUNT])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_DISCOUNT])

                # Validate category_id
                try:
                    categoryId = int(product["category_id"])
                    if categoryId < 0:
                        raise ValueError(Message[Constants.MSG_INVALID_CATEGORY_ID])
                except ValueError as e:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CATEGORY_ID])

                # Validate image
                image = ""
                if "image" in request.files:
                    file = request.files["image"]
                    if file and imghdr.what(file) != None:
                        # Hash filename to MD5
                        hash = hashlib.md5()
                        hash.update((secure_filename(file.filename) + str(datetime.now())).encode())
                        filename = hash.hexdigest() + "." + secure_filename(file.filename).split(".")[len(secure_filename(file.filename).split(".")) - 1]

                        # Store file
                        image = productPath + filename
                        file.save(image)
                        product["image"] = image
                    else:
                        return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_IMAGE])
                else:
                    product["image"] = ""
                print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa: ", oldAvatar)
                if oldAvatar != "":
                    os.remove(oldAvatar)
                                            
                # Update new product
                err = self.pgsql.UpdateProduct(product)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                
                # Handle successfull response
                return self.handleResponse(HTTPStatus.OK.value, "")
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_ID])
        
        @product.route('/products/<id>', methods=['DELETE'])
        def ProductDelete(id):
            try:
                # Get product by id
                id = int(id)
                product, err = self.pgsql.GetProductById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if product == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_PRODUCT_NOT_FOUND])

                err = self.pgsql.DeleteProduct(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if product["image"] != "":
                    os.remove(product["image"])
                    
                # Handle successfull response
                return self.handleResponse(HTTPStatus.OK.value, id)
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_ID])
        
        return (product)
