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

class UserController(BaseController):
    """
    Quản lý tài khoản người dùng
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

    def UserBlueprint(self, avataPath):
        """
        Tạo Blueprint dùng để đăng kí cho thư viện flask
        Input:
            avatarPath (string): đường dẫn thư mục chứa avatar của người dùng
        Output:
            Blueprint
        """
        user = Blueprint('user', __name__)

        @user.route('/users/<id>', methods=['GET'])
        def UserView(id):
            """
            Lấy thông tin tài khoản người dùng theo id
            Input:
                id (int): id của người dùng
            Output:
                Response
            """
            try:
                # Get user by id
                id = int(id)
                res, err = self.pgsql.GetUserById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if res == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_USER_NOT_FOUND])
                    
                # Handle successfull response
                res["password"] = ""
                res["created_at"] = str(res["created_at"])
                return self.handleResponse(HTTPStatus.OK.value, res)
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_USER_ID])

        @user.route('/users/<id>', methods=['PUT'])
        def UserUpdate(id):
            """
            Cập nhật thông tin tài khoản người dùng theo id
            Input:
                id (int): id của người dùng
            Output:
                Response
            """
            try:
                # Get user by id
                id = int(id)
                user, err = self.pgsql.GetUserById(id)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)

                if user == None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, Message[Constants.MSG_USER_NOT_FOUND])

                # Get updated field
                oldUsername = user["username"]
                oldAvatar = user["image"]
                for key, value in request.form.items():
                    if key in user and key != "id" and key != "password":
                        user[key] = value

                # Validate image
                if "image" in request.files:
                    file = request.files["image"]
                    if file and imghdr.what(file) != None:
                        # Hash filename to MD5
                        hash = hashlib.md5()
                        hash.update((secure_filename(file.filename) + str(datetime.now())).encode())
                        filename = hash.hexdigest() + "." + secure_filename(file.filename).split(".")[len(secure_filename(file.filename).split(".")) - 1]

                        # Store file
                        image = avataPath + filename
                        file.save(image)
                        user["image"] = image
                    else:
                        return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_IMAGE])
                else:
                    user["image"] = ""
                if oldAvatar != "":
                    os.remove(oldAvatar)

                # Check username if existed
                if oldUsername != user["username"]:
                    res, err = self.pgsql.GetUserByUsername(user["username"])
                    if err != None:
                        return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                    if res != None:
                        return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_USERNAME])

                # Validate role
                if user["role"] != "admin" and user["role"] != "operator":
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_ROLE])

                # Update user
                err = self.pgsql.UpdateUser(user)
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                    
                # Handle successfull response
                user["password"] = ""
                user["created_at"] = str(user["created_at"])
                return self.handleResponse(HTTPStatus.OK.value, user)
            except ValueError as e:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_USER_ID])       
            
        return (user)