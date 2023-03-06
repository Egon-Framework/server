"""API resources for API version 1"""

from dataclasses import asdict

from fastapi import HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi_restful import Resource
from sqlalchemy import select

from egon_server import orm

__api_version__ = '1.0'


class Pipeline(Resource):
    """Resource for pipeline metadata"""

    async def get(self, pipelineId: str) -> Response:
        """Fetch data describing an egon pipeline

        Args:
            pipelineId: The pipeline ID assigned by Egon
        """

        query = select(orm.Pipeline).where(orm.Pipeline.egon_id == pipelineId)
        async with orm.DBConnection.session_maker() as session:
            result = await session.execute(query)
            db_object = result.scalars().first()

        if db_object is None:
            raise HTTPException(status_code=404)

        return JSONResponse(asdict(db_object))


class Node(Resource):
    """Resource for node metadata"""

    async def get(self, nodeId: str) -> Response:
        """Fetch data describing an egon node

        Args:
            nodeId: The node ID assigned by Egon
        """

        query = select(orm.Node).where(orm.Node.egon_id == nodeId)
        async with orm.DBConnection.session_maker() as session:
            result = await session.execute(query)
            db_object = result.scalars().first()

        if db_object is None:
            raise HTTPException(status_code=404)

        return JSONResponse(asdict(db_object))
