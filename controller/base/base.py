from flask import jsonify, Response
import json


class BaseController():
    """
    Xử lý kết quả trả về của các API
    """
    def handleError(self, code, msg):
        """
        Xử lý lỗi trả về của các API
        Input:
	        code (int): HTTP status code
	        msg (string): tin nhắn
        Output:
            Response
        """
        res = {
            "status": code,
            "message": msg,
            "data": None
        }
        return Response(response=json.dumps(res), status=code, mimetype='application/json')

    def handleResponseList(self, code, limit, offset, total, data):
        """
        Xử lý kết quả trả về của các API có chức năng phân trang
        Input:
	        code (int): HTTP status code
	        limit (int): giới hạn đối tượng trong 1 trang
	        offset (int): bước nhảy khi phân trang 
	        total (int): tổng số đối tượng
	        data (array dictionary): dữ liệu trả về trong Response
        Output:
            Response
        """
        res = {
            "status": code,
            "message": "",
            "data": {
                "data": data,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
        return Response(response=json.dumps(res), status=code, mimetype='application/json')

    def handleResponse(self, code, data):
        """
        Xử lý kết quả trả về của các API khác không có chức năng phân trang
        Input:
	        code (int): HTTP status code
	        data (dictionary): dữ liệu trả về trong Response
        Output:
            Response
        """
        res = {
            "status": code,
            "message": "",
            "data": data
        }
        return Response(response=json.dumps(res), status=code, mimetype='application/json')
