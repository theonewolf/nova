# Copyright (C) 2014, Carnegie Mellon University
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

from nova import db
from nova import exception
from nova.objects import base
from nova.objects import fields


class IntrospectedEntity(base.NovaPersistentObject, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'instance_uuid': fields.UUIDField(),
        'drive_id': fields.StringField(nullable=False),
        'introspection_target': fields.StringField(nullable=False),
    }

    @staticmethod
    def _from_db_object(context, ie, db_ie):
        for field in ie.fields:
            ie[field] = db_ie[field]
        ie._context = context
        ie.obj_reset_changes()
        return ie

    @base.remotable_classmethod
    def get_by_id(cls, context, ie_id):
        db_ie = db.introspected_entity_get(context, ie_id)
        if db_ie:
            return cls._from_db_object(context, cls(), db_ie)

    @base.remotable
    def create(self, context):
        if self.obj_attr_is_set('id'):
            raise exception.ObjectActionError(action='create',
                                              reason='already created')
        updates = self.obj_get_changes()
        db_ie = db.introspected_entity_create(context, updates)
        self._from_db_object(context, self, db_ie)

    @base.remotable_classmethod
    def delete_by_instance_uuid(cls, context, instance_uuid):
        db.introspected_entity_delete_by_instance(context, instance_uuid)

    @base.remotable_classmethod
    def delete_by_id(cls, context, ie_id):
        db.introspected_entity_delete_by_id(context, ie_id)


class IntrospectedEntityList(base.ObjectListBase, base.NovaObject):
    # Version 1.0: Initial version
    VERSION = '1.0'
    fields = {
        'objects': fields.ListOfObjectsField('IntrospectedEntity'),
    }
    child_versions = {
        '1.0': '1.0',
    }

    @base.remotable_classmethod
    def get_all(cls, context):
        db_ies = db.introspected_entity_get_all(context)
        return base.obj_make_list(context, cls(), IntrospectedEntity, db_ies)

    @base.remotable_classmethod
    def get_by_instance_uuid(cls, context, instance_uuid, use_slave=False):
        db_ies = db.introspected_entity_get_by_instance(context,
                instance_uuid, use_slave=use_slave)
        return base.obj_make_list(context, cls(), IntrospectedEntity, db_ies)
