from flask import jsonify, json
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, status_code, code, message, fields=None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.fields = fields or {}


def register_error_handlers(app):
    @app.errorhandler(NotImplementedError)
    def unfinished(error):
        return jsonify(error={"code": "unfinished_exercise",
                              "message": str(error), "fields": {}}), 501

    @app.errorhandler(ApiError)
    def api_error(error):
        return jsonify(error={
            "code": error.code,
            "message": error.message,
            "fields": error.fields,
        }), error.status_code

    @app.errorhandler(HTTPException)
    def http_error(error):
        # Preserve status and headers, including Allow on a 405.
        response = error.get_response()
        codes = {
            400: "bad_request", 404: "not_found",
            405: "method_not_allowed", 415: "unsupported_media_type",
            500: "internal_error",
        }
        messages = {
            400: "Malformed or missing JSON body",
            404: "Route not found",
            405: "Method not allowed for this route",
            415: "Send a JSON Content-Type",
            500: "Unexpected server error",
        }
        response.data = json.dumps({"error": {
            "code": codes.get(error.code, "http_error"),
            "message": messages.get(error.code, error.name),
            "fields": {},
        }})
        response.content_type = "application/json"
        return response
