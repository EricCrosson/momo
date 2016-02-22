#!/usr/bin/env python
# Written by Eric Crosson
# 2016-02-16

import nmap

# TODO: document


class nmapDetector(Detector):


    def __init__(self, target):
        self.target = target
        self.nm = nmap.PortScanner()
        # TODO: start a thread to detect and set self.host_present
        # block until initial detector succeeds


    def scan_for_host(self):
        """Return True if method name condition is met."""
        results = nm.scan(hosts='192.168.1.0/24', arguments='-sP')
        # TODO: parametrize
        for i in results['scan'].keys():
            if results['scan'][i]['hostnames'][0]['name'] == self.target:
                return True
        return False


    def scan_loop(self):
        while True:
            self.host_present = self.scan_for_host()
