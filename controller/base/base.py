from flask import jsonify


class BaseController():
    def handleError(self, code, msg):
        return jsonify(
            {
                "status": code,
                "message": msg,
                "data": None
            }
        )

    def handleResponseList(self, code, limit, offset, total, data):
        return jsonify(
            {
                "status": code,
                "message": "",
                "data": {
                    "data": data,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
            }
        )
