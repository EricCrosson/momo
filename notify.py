#!/usr/bin/env python
# Written by Eric Crosson
# 2016-02-09

# TODO: turn off webcam if eric is home

import os
import nmap
import time
import glob
import psutil
import subprocess
from pushbullet import Pushbullet

api_key='o.d6KVGP94jqzGR2arn8h4tPtnRNSggur1'
pb = Pushbullet(api_key)

motion_dir = '/tmp/motion'
nm = nmap.PortScanner()

def name(pic):
    """Generate a name for the given picture."""
    return time.strftime("%Y-%m-%d %H:%M")


def is_erics_iphone_in_home_network():
    """Return True if method name condition is met."""
    results = nm.scan(hosts='192.168.1.0/24', arguments='-sP')
    # TODO: parametrize
    for i in results['scan'].keys():
        if results['scan'][i]['hostnames'][0]['name'] == 'Erics-iPhone.att.net':
            return True
    return False


def process_running(name):
    """Returns True if named process is running."""
    return name in [i.name() for i in psutil.process_iter()]


def ensure_motion_is_running():
    """Start motion if not running and give it a sec to boot up."""
    if not process_running('motion'):
        print('Starting motion')
        return subprocess.check_output('sudo motion'.split()).decode('utf-8')


def kill_motion():
    """Ensure the motion process is not active (blue webcam light off)."""
    if process_running('motion'):
        print('Stopping motion')
        return subprocess.check_output('sudo killall motion'.split()).decode('utf-8')


while (True):
    if (not is_erics_iphone_in_home_network()):
        ensure_motion_is_running()
        for jpg in glob.glob(os.path.join(motion_dir, '*.jpg')):
            # TODO: log instead
            with open(jpg, 'rb') as pic:
                # TODO: only push if cell phone not in house wifi
                file_data = pb.upload_file(pic, name(pic))
                push = pb.push_file(**file_data)
                # TODO: try-catch with logging
                os.remove(jpg)
                # Clean up motion_dir: discard swfs for room
        	for swf in glob.glob(os.path.join(motion_dir, '*.swf')):
                    os.remove(swf)
    else:
        kill_motion()
        for file in glob.glob(os.path.join(motion_dir, '*')):
            os.remove(file)
        # TODO: log instead
        print('Eric is home -- sleeping')
    time.sleep(30)
