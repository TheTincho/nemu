#!/usr/bin/env python
# vim:ts=4:sw=4:et:ai:sts=4

import os

try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
#yaml.load(stream, Loader = Loader)

class __Config(object):
    def __init__(self):
        self.run_as = None

config = __Config()

def get_nodes():
    return set()
def set_cleanup_hooks(on_exit = False, on_signals = []):
    pass

class Node(object):
    def __init__(self):
        self.slave = SlaveNode()
        self.valid = True
    def add_if(self, mac_address = None, mtu = None):
        return Interface(mac_address, mtu)
    def add_route(self, prefix, prefix_len, nexthop = None, interface = None):
        assert nexthop or interface
    def add_default_route(self, nexthop, interface = None):
        return self.add_route('0.0.0.0', 0, nexthop, interface)
    def start_process(self, args):
        return Process()
    def run_process(self, args):
        return ("", "")
    def get_routes(self):
        return set()

class Link(object):
    def connect(self, iface):
        pass

class Interface(object):
    def __init__(self, mac_address = None, mtu = None):
        self.name = None
        self.mac_address = mac_address
        self.mtu = mtu
        self.valid = True
    def add_v4_address(self, address, prefix_len, broadcast = None):
        pass
    def add_v6_address(self, address, prefix_len):
        pass

class Process(object):
    def __init__(self):
        self.pid = os.getpid()
        self.valid = True

import os, socket, sys, unshare
class SlaveNode(object):
    def __init__(self):
        (s0, s1) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        ppid = os.getpid()
        pid = os.fork()
        if pid:
            helo = s0.recv(4096).rstrip().split(None, 1)
            if int(helo[0]) / 100 != 2:
                raise RuntimeError("Failed to start slave node: %s" % helo[1])
            self.pid = pid
            self.sock = s0
            s1.close()
            return
        try:
            s0.close()
            #unshare.unshare(unshare.CLONE_NEWNET)
            self.sock = s1.makefile("r+")
            self.ppid = ppid
            self.run()
        except BaseException, e:
            s1.send("500 %s\n" % str(e))
            sys.stderr.write("Error starting slave node: %s\n" % str(e))
            os._exit(1)
        os._exit(0)
    def run(self):
        self.sock.write("220 Hello.\n");
        while True:
            line = self.sock.readline()
            if not line:
                break
            self.sock.write("ECHO: %s\n" % line.rstrip())

