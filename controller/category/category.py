from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants

class CategoryController(BaseController):
    """
    Xử lý các chức năng liên quan đến danh mục sản phẩm
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

    def CategoryBlueprint(self):
        """
        Tạo Blueprint dùng để đăng kí cho thư viện flask
        Input:
        Output:
            Blueprint
        """
        category = Blueprint('category', __name__)

        @category.route('/categories', methods=['GET'])
        def CategoryList():
            """
            Lấy danh sách danh mục sản phẩm
            Input:
            Output:
                Response
            """
            # Get category list
            res, err = self.pgsql.CategoryList()
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, res)

        @category.route('/categories', methods=['POST'])
        def CategoryAdd():
            """
            Tạo danh mục sản phẩm
            Input:
            Output:
                Response
            """
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

        @category.route('/categories/<id>', methods=['PUT'])
        def CategoryUpdate(id):
            """
            Cập nhật danh mục sản phẩm theo id
            Input:
                id (int): id của danh mục sản phẩm
            Output:
                Response
            """
            try:
                # Get product by id
                id = int(id)
                category, err = self.pgsql.GetCategoryById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if category == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_CATEGORY_NOT_FOUND])

                # Get updated field
                oldName = category["name"]
                for key, value in request.form.items():
                    if key in category and key != "id":
                        category[key] = value

                # Check name if existed
                if oldName != category["name"]:
                    res, err = self.pgsql.GetCategoryByName(category["name"])
                    if err != None:
                        return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                    if res != None:
                        return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_CATEGORY_NAME])

                # Update category
                err = self.pgsql.UpdateCategory(category)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                
                # Handle successfull response
                return self.handleResponse(HTTPStatus.OK.value, "")
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CATEGORY_ID])

        @category.route('/categories/<id>', methods=['DELETE'])
        def CategoryDelete(id):
            """
            Xóa danh mục sản phẩm theo id
            Input:
                id (int): id của danh mục sản phẩm
            Output:
                Response
            """
            try:
                # Get category by id
                id = int(id)
                category, err = self.pgsql.GetCategoryById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if category == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_CATEGORY_NOT_FOUND])

                # Count products linked with category
                count, err = self.pgsql.CountProductsLinkWithCategory(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if category != None and count["count"] > 0:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_CANNOT_DELETE_CATEGORY])               

                # Delete category
                err = self.pgsql.DeleteCategory(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                    
                # Handle successfull response
                return self.handleResponse(HTTPStatus.OK.value, id)
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PRODUCT_ID])
            
        return (category)