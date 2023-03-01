"""Common API resources used across several API versions."""

from flask import Response
from flask_restful import Resource


class Description(Resource):
    """Resource for getting the API description"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return Response(
            'The Egon Framework status API. '
            'See https://egon-framework.github.io/status-api/ for more details.')
