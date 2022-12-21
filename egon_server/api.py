from flask import Flask, jsonify, Response
from flask_restful import Resource, Api

__api_version__ = '0.0.1'

flask_app = Flask(__name__)
api = Api(flask_app)


class Description(Resource):
    """Resource for getting the API description"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return Response(
            'The Egon Framework status API. '
            'See https://egon-framework.github.io/status-api/ for more details.')


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


api.add_resource(Description, '/')
api.add_resource(Health, '/health')
api.add_resource(Version, '/version')
