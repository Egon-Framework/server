"""URL routing for the application's REST API."""

from flask import Flask
from flask_restful import Api

from . import resources

flask_app = Flask(__name__)

# Create a new API instance
api = Api(flask_app)
api.add_resource(resources.common.Description, '/')

# Add V1 API endpoints
api.add_resource(resources.v1.Health, '/v1/health')
api.add_resource(resources.v1.Version, '/v1/version')
