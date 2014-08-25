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
from nova import exception
from nova.openstack.common.gettextutils import _
from nova.openstack.common import log as logging


LOG = logging.getLogger(__name__)
authorize = extensions.extension_authorizer('compute', 'introspection')

def _translate_introspected_entity_view(ie_info):
    """Maps keys for introspected entity details view."""
    return {
            'drive_id'                  : ie_info['drive_id'],
            'introspected_entity_id'    : ie_info['id'],
            'target'                    : ie_info['introspection_target']
           }

class IntrospectionController(object):
    """The  introspection API controller for the OpenStack API."""

    def __init__(self):
        self.compute_api = compute.API()
        self.introspection_api = compute.api.IntrospectionAPI()
        LOG.info('Introspection Extension API Activated!')
        super(IntrospectionController, self).__init__()

    def index(self, req, server_id):
        """Returns the list of introspected entities for a given instance."""

        return self._items(req, server_id, entity_maker=
                           _translate_introspected_entity_view)

    def show(self, req, server_id, id):
        """Return data about the given entity's introspection."""

        context = req.environ['nova.context']
        authorize(context)

        ie_id = id
        try:
            self.compute_api.get(context, server_id)
        except exception.NotFound:
            raise exc.HTTPNotFound()

        try:
            ie_info = self.introspection_api.get_introspected_entity(context, ie_id)
        except exception.NotFound:
            raise exc.HTTPNotFound()

        if ie_info['instance_uuid'] != server_id:
            raise exc.HTTPNotFound()

        return {'introspected_entity' : _translate_introspected_entity_view(
                ie_info)}

    def create(self, req, server_id, body):
        """Activate introspection for a given aspect of an instance."""
        context = req.environ['nova.context']
        authorize(context)

        drive_id = None
        target = None

        if body:
            ie = body['introspection_entity']
            drive_id = ie.get('drive_id', None)
            target = ie.get('introspection_target', None)

        if not drive_id or not target:
            raise exc.HTTPBadRequest()

        try:
            instance = self.compute_api.get(context, server_id,
                                            want_objects=True)
            LOG.audit(_("Introspect entity"), instance=instance)
            ie = self.introspection_api.activate_introspection(context,
                                                               server_id,
                                                               drive_id,
                                                               target)
        except NotImplementedError:
            msg = _("Compute driver does not support this function.")
            raise exc.HTTPNotImplemented(explanation=msg)

        return self.show(req, server_id, ie['id'])

    def delete(self, req, server_id, id):
        """Deactivate introspection for a given aspect of an instance."""
        context = req.environ['nova.context']
        authorize(context)
        ie_id = id

        try:
            instance = self.compute_api.get(context, server_id,
                                            want_objects=True)
            LOG.audit(_("Deactivate introspection %s"), ie_id,
                      instance=instance)
        except exception.NotFound:
            raise exc.HTTPNotFound()

        try:
            self.introspection_api.deactivate_introspection(context, instance,
                                                            ie_id=ie_id)
        except NotImplementedError:
            msg = _("Compute driver does not support this function.")
            raise exc.HTTPNotImplemented(explanation=msg)
        
        return webob.Response(status_int=202)

    def _items(self, req, server_id, entity_maker):
        """Returns a list of transformed introspected entities"""
        context = req.environ['nova.context']
        authorize(context)

        results = []

        try:
            data = self.introspection_api.list_introspected_entities(context,
                                                                     server_id)
        except exception.NotFound:
            raise exc.HTTPNotFound()
        except NotImplementedError:
            msg = _("Compute driver does not support this function.")
            raise exc.HTTPNotImplemented(explanation=msg)

        results = [entity_maker(ie) for ie in data]

        return {'introspected_entities' : results}

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
