# Copyright 2014 Carnegie Mellon University
# Author: Wolfgang Richter <wolf@cs.cmu.edu>
#
#
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

from nova.virt.libvirt import driver 

class IntrospectionDriver(driver.LibvirtDriver):
    def __init__(self, virtapi, read_only=False):
        super(IntrospectionDriver, self).__init__(virtapi)
        driver.LOG.info('IntrospectionDriver compute driver activated!')

    def activate_introspection(self, instance, drive_id, introspection_target):
        driver.LOG.info('IntrospectionDriver activate_introspection() called.')

    def deactivate_introspection(self, instance, drive_id, introspection_target):
        driver.LOG.info('IntrospectionDriver deactivate_introspection() called.')
