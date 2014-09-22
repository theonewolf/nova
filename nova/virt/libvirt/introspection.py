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



from nova import utils
from nova.virt.libvirt import driver 



#constants/globals
QMP_COMMAND = '{"execute" : "drive-backup", "arguments" : {"device" : "drive-virtio-disk0", "mode" : "existing", "format" : "raw", "target" : "nbd://127.0.0.1:%d", "sync" : "stream"} }'
libvirt = None
libvirt_qemu = None

# helper functions
def check_port(port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setblocking(1)
    try:
        sock.connect(('127.0.0.1', port))
    except:
        return False
    return True

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

def reset_redis(db=None):
    if db != None:
        CMD = ['redis-cli']
        CMD.append('-n')
        CMD.append(str(db))
        CMD.append('flushdb')
        Popen(CMD).wait()
        return

    CMD = ['redis-cli']
    CMD.append('FLUSHALL')

    driver.LOG.info('IntrospectionDriver reset_redis() executing: %s.', CMD)
    Popen(CMD).wait()

def setup_crawl(uuid):
    # SETUP
    (out, err) = utils.execute('qemu-nbd',
                               '-r',
                               '-c',
                               '/dev/nbd0',
                               '/var/lib/nova/instances/%s/disk' % (uuid),
                               run_as_root=True)
    driver.LOG.info('IntrospectionDriver setup_crawl() connecting block device: stdout=(%s), stderr=(%s).', out, err)
    
    (out, err) = utils.execute('chmod', '664', '/dev/nbd0', run_as_root=True)
    driver.LOG.info('IntrospectionDriver setup_crawl() chmod 664: stdout=(%s), stderr=(%s).', out, err)

    # CRAWL 
    CMD = ['/home/wolf/gammaray_bin/gray-crawler']
    CMD.append('/dev/nbd0')
    CMD.append('/var/lib/nova/instances/%s/disk.bson' % (uuid))
    driver.LOG.info('IntrospectionDriver setup_crawl() executing: %s.', CMD)

    p3 = Popen(CMD)
    p3.wait()


    # TEARDOWN
    (out, err) = utils.execute('chmod', '660', '/dev/nbd0', run_as_root=True)
    driver.LOG.info('IntrospectionDriver setup_crawl() chmod 660: stdout=(%s), stderr=(%s).', out, err)

    (out, err) = utils.execute('qemu-nbd',
                               '-d',
                               '/dev/nbd0',
                               run_as_root=True)
    driver.LOG.info('IntrospectionDriver setup_crawl() deactivating block device: stdout=(%s), stderr=(%s).', out, err)

def setup_introspection(uuid, db):
    CMD = ['/home/wolf/gammaray_bin/gray-inferencer']
    CMD.append('/var/lib/nova/instances/%s/disk.bson' % (uuid))
    CMD.append(str(db))
    CMD.append(uuid)

    driver.LOG.info('IntrospectionDriver setup_introspection() executing: %s.', CMD)

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
            sleep(0.001)

        sleep(5) # FIXME sync with nbd process...
        
        cmd = QMP_COMMAND % nbdport

        instance_name = instance['name']
        virt_dom = self._lookup_by_name(instance_name)
        QMP_MODE = libvirt_qemu.VIR_DOMAIN_QEMU_MONITOR_COMMAND_DEFAULT

        driver.LOG.info('QMP Command: %s' % cmd)

        driver.LOG.info('QMP Command Result: %s' %
                 str(libvirt_qemu.qemuMonitorCommand(virt_dom, cmd, QMP_MODE)))

    def activate_introspection(self, context, instance, drive_id,
                               introspection_target):
        driver.LOG.info('IntrospectionDriver activate_introspection().')
        nbdport = assign_port(9000, 15000)
        reset_redis()
        setup_nbd(0, nbdport) # FIXME hard-coded ports
        self.exec_qmp(instance, nbdport)
        setup_crawl(instance['uuid'])
        setup_introspection(instance['uuid'], 0)

    def deactivate_introspection(self, context, instance, drive_id,
                                 introspection_target):
        driver.LOG.info('IntrospectionDriver deactivate_introspection().')
