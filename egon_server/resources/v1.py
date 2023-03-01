"""API resources for version 1 of the API"""

from flask import Response, jsonify
from flask_restful import Resource

__api_version__ = '1.0'


class Health(Resource):
    """Resource for checking API health"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return Response(status=200)


class Version(Resource):
    """Resource for checking the API version"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        major, minor, *other = __api_version__.split('.')
        return jsonify({'version': f'{major}.{minor}'})
