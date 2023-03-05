"""API resources for API version 1"""

from fastapi import HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi_restful import Resource

from egon_server import orm

__api_version__ = '1.0'


class Version(Resource):
    """Resource for checking the API version"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        major_version = __api_version__.split('.')[0]
        return JSONResponse({'version': major_version})


class Pipeline(Resource):
    """Resource for pipeline metadata"""

    def get(self, pipelineId) -> Response:
        """Fetch data describing an egon pipeline

        Args:
            pipelineId: The pipeline ID assigned by Egon
        """

        db_object = orm.Pipeline.query.filter(
            orm.Pipeline.egon_id == pipelineId
        ).first()

        if db_object is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return JSONResponse(db_object)


class Node(Resource):
    """Resource for node metadata"""

    def get(self, nodeId) -> Response:
        """Fetch data describing an egon node

        Args:
            nodeId: The node ID assigned by Egon
        """

        db_object = orm.Node.query.filter(
            orm.Node.egon_id == nodeId
        ).first()

        if db_object is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return JSONResponse(db_object)
