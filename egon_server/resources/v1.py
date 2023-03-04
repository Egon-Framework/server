"""API resources for version 1 of the API"""

from flask import abort, Response, jsonify
from flask_restful import Resource

from egon_server import orm

__api_version__ = '1.0'


class Version(Resource):
    """Resource for checking the API version"""

    def get(self) -> Response:
        """Handle an incoming GET request"""

        major, *other = __api_version__.split('.')
        return jsonify({'version': major})


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
            abort(404)

        return jsonify(db_object)


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
            abort(404)

        return jsonify(db_object)
