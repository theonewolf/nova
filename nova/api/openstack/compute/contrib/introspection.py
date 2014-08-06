# Copyright 2014 Carnegie Mellon University 
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""The introspection extension."""

import webob
from webob import exc

from nova.api.openstack import extensions
from nova import compute
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging


LOG = logging.getLogger(__name__)
authorize = extensions.extension_authorizer('compute', 'introspection')

class IntrospectionController(object):
    """The  introspection API controller for the OpenStack API."""

    def __init__(self):
        self.compute_api = compute.API()
        LOG.info('Introspection Extension API Activated!')
        super(IntrospectionController, self).__init__()

    def index(self, req, server_id):
        """Returns the list of introspected entities for a given instance."""

        msg = _("index currently not implemented.")
        raise exc.HTTPNotImplemented(explanation=msg)

    def show(self, req, server_id, id):
        """Return data about the given entity's introspection."""

        msg = _("show currently not implemented.")
        raise exc.HTTPNotImplemented(explanation=msg)

    def create(self, req, server_id, body):
        """Activate introspection for a given aspect of an instance."""

        msg = _("activate currently not implemented.")
        raise exc.HTTPNotImplemented(explanation=msg)

    def delete(self, req, server_id, id):
        """Deactivate introspection for a given aspect of an instance."""

        msg = _("activate currently not implemented.")
        raise exc.HTTPNotImplemented(explanation=msg)

class Introspection(extensions.ExtensionDescriptor):
    """Introspection support."""

    name = "Introspect"
    alias = "os-introspect"
    namespace = "http://docs.openstack.org/compute/ext/introspection/api/v1"
    updated = "2014-08-01T00:00:00+00:00"

    def get_resources(self):
        resources = []

        res = extensions.ResourceExtension('os-introspection',
                                           IntrospectionController(),
                                           parent=dict(
                                               member_name='server',
                                               collection_name='servers'))
        resources.append(res)

        return resources
