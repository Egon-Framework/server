"""Common API resources used across several API versions."""

from fastapi.responses import Response
from fastapi_restful import Resource


class Health(Resource):
    """Resource for checking API health"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return Response(status_code=200)


class Description(Resource):
    """Resource for getting the API description"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return Response('The Egon Status API.')
