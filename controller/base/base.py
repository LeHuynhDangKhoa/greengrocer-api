from flask import jsonify, Response
import json


class BaseController():
    def handleError(self, code, msg):
        res = {
            "status": code,
            "message": msg,
            "data": None
        }
        return Response(response=json.dumps(res), status=code, mimetype='application/json')

    def handleResponseList(self, code, limit, offset, total, data):
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
        res = {
            "status": code,
            "message": "",
            "data": data
        }
        return Response(response=json.dumps(res), status=code, mimetype='application/json')
