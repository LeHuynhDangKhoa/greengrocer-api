from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from werkzeug.utils import secure_filename

class CategoryController(BaseController):
    def __init__(self, pgsql: PGSQL):
        self.pgsql = pgsql

    def CategoryBlueprint(self):
        category = Blueprint('category', __name__)

        @category.route('/categories', methods=['GET'])
        def CategoryList():
            # Get category list
            res, err = self.pgsql.CategoryList()
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, res)

        @category.route('/categories', methods=['POST'])
        def CategoryAdd():
            values = []
            # Validate name
            if "name" in request.json:
                # Check name if existed
                res, err = self.pgsql.GetCategoryByName(request.json["name"])
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                if res != None:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_CATEGORY_NAME])
                values.append(request.json["name"])
            else:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_CATEGORY_NAME])
                    
            # Inert new category
            err = self.pgsql.InsertNewCategory(values)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, "")
            
        return (category)