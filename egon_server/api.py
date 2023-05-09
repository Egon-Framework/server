"""URL routing for the application's REST API."""

from fastapi import FastAPI
from fastapi_restful import Api

from . import resources


class AppFactory:
    """Factory class for creating new FastAPI applications"""

    def __new__(cls, *args: any, openapi_url=None, import_name: str = 'egon-server', **kwargs) -> FastAPI:
        """Create a new FastAPI application

        Accepts the same positional and keyword arguments as the ``fastapi.FastAPI`` object

        Returns:
           A new FastAPI application instance with established API endpoints
        """

        app = FastAPI(*args, import_name=import_name, openapi_url=openapi_url, **kwargs)
        api = Api(app)

        api.add_resource(resources.common.Description(), '/')
        api.add_resource(resources.common.Health(), '/health')
        cls.add_v1_endpoints(api, endpoint_root='/v1')
        return app

    @staticmethod
    def _clean_endpoint_root(endpoint_root: str) -> str:
        """Make sure endpoint roots start with a single slash and end with no slashes"""

        return '/' + f'{endpoint_root}'.strip('/')

    @classmethod
    def add_v1_endpoints(cls, api: Api, endpoint_root: str = '') -> None:
        """Add endpoints for version 1 of the API specification"""

        endpoint_root = cls._clean_endpoint_root(endpoint_root)
        api.add_resource(resources.common.Version(1), f'{endpoint_root}/version')
        api.add_resource(resources.v1.Pipeline(), endpoint_root + '/pipeline/{pipelineId}')
        api.add_resource(resources.v1.Node(), endpoint_root + '/node/{nodeId}/')
