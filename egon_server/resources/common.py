"""Common API resources used across several API versions."""

from fastapi.responses import Response, JSONResponse
from fastapi_restful import Resource


class Version(Resource):
    """Resource for checking the API version"""

    def __init__(self, version: int) -> None:
        """Initialize the resource for a given version number:

        Args:
            version: The version number
        """

        self._version = version

    def get(self) -> Response:
        """Handle an incoming GET request"""

        return JSONResponse({'version': self._version})


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
