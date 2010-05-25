#!/usr/bin/env python
# vim:ts=4:sw=4:et:ai:sts=4

import netns
import os
import signal
import subprocess
import sys
import time
import unittest

class TestNode(unittest.TestCase):
#    def setUp(self):
#        pass
    def test_node(self):
        node = netns.Node()
        self.failIfEqual(node.pid, os.getpid())
        self.failIfEqual(node.pid, None)
        # check if it really exists
        os.kill(node.pid, 0)

        nodes = netns.get_nodes()
        self.assertEquals(nodes, set([node]))
        
        # Test that netns recognises a fork
        chld = os.fork()
        if chld == 0:
            if len(netns.get_nodes()) == 0:
                sys.exit(0)
            sys.exit(1)
        (pid, exitcode) = os.waitpid(chld, 0)
        self.assertEquals(exitcode, 0)

    def test_routing(self):
        node = netns.Node()

    def test_cleanup(self):
        def create_stuff():
            a = netns.Node()
            b = netns.Node()
            ifa = a.add_if()
            ifb = b.add_if()
            link = netns.Link()
            link.connect(ifa)
            link.connect(ifb)
        def get_devs():
            ipcmd = subprocess.Popen(["ip", "-o", "link", "list"],
                    stdout = subprocess.PIPE)
            (outdata, errdata) = ipcmd.communicate()
            ipcmd.wait()
            return outdata.split("\n")

        orig_devs = len(get_devs())
        create_stuff()
        self.assertEquals(netns.get_nodes(), set())
        self.assertEquals(orig_devs, len(get_devs()))

        # Test at_exit hooks
        orig_devs = len(get_devs())
        chld = os.fork()
        if chld == 0:
            netns.set_cleanup_hooks(on_exit = True, on_signals = [])
            create_stuff()
            sys.exit()
        os.waitpid(chld, 0)
        self.assertEquals(orig_devs, len(get_devs()))

        # Test signal hooks
        orig_devs = len(get_devs())
        chld = os.fork()
        if chld == 0:
            netns.set_cleanup_hooks(on_exit = False,
                    on_signals = [signal.SIGTERM])
            create_stuff()
            while True:
                time.sleep(10)
        os.kill(chld)
        os.waitpid(chld, 0)
        self.assertEquals(orig_devs, len(get_devs()))

if __name__ == '__main__':
    unittest.main()
