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

from random import randint
from socket import AF_INET, SOCK_STREAM, socket
from subprocess import Popen
from time import sleep



from nova.virt.libvirt import driver 



#constants/globals
QMP_COMMAND = 'drive-backup sync=stream device=virtio0 ' + \
              'target=nbd://127.0.0.1:%d/ format=raw mode=existing'
libvirt = None
libvirt_qemu = None

# helper functions
def check_port(port):
    sock = socket(AF_INET, SOCK_STREAM)
    return sock.connect_ex(('127.0.0.1', port)) == 0

def assign_port(a, b):
    testport = randint(a, b)
    while check_port(testport):
        testport = randint(a, b)
    return testport

def setup_nbd(db, port):
    CMD = ['/home/wolf/gammaray_bin/test/nbd-queuer-test']
    CMD.append('null')
    CMD.append('127.0.0.1')
    CMD.append('6379')
    CMD.append(str(db))
    CMD.append('107374182400')
    CMD.append('0.0.0.0')
    CMD.append(str(port))
    CMD.append('y')
    
    return Popen(CMD)



class IntrospectionDriver(driver.LibvirtDriver):
    def __init__(self, virtapi, read_only=False):
        super(IntrospectionDriver, self).__init__(virtapi)
        driver.LOG.info('IntrospectionDriver compute driver activated!')

        global libvirt_qemu
        if libvirt_qemu is None:
            libvirt_qemu = __import__('libvirt_qemu')

    def exec_qmp(self, instance, nbdport):
        while not check_port(nbdport):
            sleep(0.02)
        
        cmd = QMP_COMMAND % nbdport

        virt_dom = self._lookup_by_name(instance_name)
        instance_name = instance['name']
        HMP_MODE = libvirt_qemu.VIR_DOMAIN_QEMU_MONITOR_COMMAND_HMP

        driver.LOG.info('QMP Command Result: %s' %
                 str(libvirt_qemu.qemuMonitorCommand(virt_dom, cmd, HMP_MODE)))

    def activate_introspection(self, context, instance, drive_id,
                               introspection_target):
        driver.LOG.info('IntrospectionDriver activate_introspection().')
        nbdport = assign_port(9000, 15000)
        setup_nbd(0, nbdport) # FIXME hard-coded ports
        self.exec_qmp(instance, nbdport)

    def deactivate_introspection(self, context, instance, drive_id,
                                 introspection_target):
        driver.LOG.info('IntrospectionDriver deactivate_introspection().')
