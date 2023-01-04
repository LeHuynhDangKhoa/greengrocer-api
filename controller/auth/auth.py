from flask import Blueprint, request
from database.pgsql import PGSQL
from controller.base.base import BaseController
from http import HTTPStatus
from pkg.message.message import Message, Constants
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime
import imghdr

class AuthController(BaseController):
    """
    Xử lý các chức năng xác thực tài khoản
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

    def AuthBlueprint(self, avataPath, bcrypt):
        """
        Tạo Blueprint dùng để đăng kí cho thư viện flask
        Input:
	        avatarPath (string): đường dẫn thư mục chứa avatar của người dùng
	        bycrypt (class Bcrypt): class dùng để mã hóa password
        Output:
            Blueprint
        """
        auth = Blueprint('auth', __name__)

        @auth.route('/register', methods=['POST'])
        def Register():
            """
            Đăng kí tài khoản mới
            Input:
            Output:
                Response
            """
            values = []
            # Validate username
            if "username" in request.form:
                # Check username if existed
                res, err = self.pgsql.GetUserByUsername(request.form["username"])
                if err != None:
                    return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
                if res != None:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EXISTED_USERNAME])
                values.append(request.form["username"])
            else:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_USERNAME])

            # Validate password
            if "password" in request.form and "confirm_password" in request.form:
                # Check password and confirm_pass if match
                if request.form["password"] != request.form["confirm_password"]:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_PASSWORD])

                # Hash password
                values.append(bcrypt.generate_password_hash(request.form["password"]).decode('utf-8'))
            else:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_PASSWORD])

            # Validate phone
            phone = ""
            if "phone" in request.form:
                phone = request.form["phone"]
            values.append(phone)

            # Validate email
            email = ""
            if "email" in request.form:
                email = request.form["email"]
            values.append(email)

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
                    image = avataPath + filename
                    file.save(image)
                else:
                    return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_IMAGE])
            values.append(image)

            # Validate role
            role = "operator"
            if "role" in request.form:
                role = request.form["role"]
            if role != "admin" and role != "operator":
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_ROLE])
            values.append(role)
                    
            # Inert new user
            err = self.pgsql.InsertNewUser(values)
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            
            # Handle successfull response
            return self.handleResponse(HTTPStatus.OK.value, "")

        @auth.route('/login', methods=['POST'])
        def Login():
            """
            Đăng nhập tài khoản
            Input:
            Output:
                Response
            """
            # Validate input
            if "username" not in request.json or "password" not in request.json:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_EMPTY_CREDENTIAL])

            # Check username if existed
            res, err = self.pgsql.GetUserByUsername(request.json["username"])
            if err != None:
                return self.handleError(HTTPStatus.INTERNAL_SERVER_ERROR.value, err)
            if res == None:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CREDENTIAL])

            # Check password
            if bcrypt.check_password_hash(res["password"], request.json["password"]) == False:
                return self.handleError(HTTPStatus.BAD_REQUEST.value, Message[Constants.MSG_INVALID_CREDENTIAL])

            # Handle successfull response
            res["password"] = ""
            res["created_at"] = str(res["created_at"])
            return self.handleResponse(HTTPStatus.OK.value, res)           
            
        return (auth)
