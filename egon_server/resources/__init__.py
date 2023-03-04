"""RESTful resources for supporting API endpoints.

API resources are organized by their corresponding API version number.
For example, resources designed to support version 1 of the API schema are
defined in the ``v1`` submodule. General resources applicable to multiple
schema versions are available under the ``common`` module.

For more information on API schema definitions, see the schema's official
`GitHub Repository <https://github.com/Egon-Framework/status-api-schema>`_.
"""

from . import common
from . import v1
