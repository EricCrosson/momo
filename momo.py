#!/usr/bin/env python
# Written by Eric Crosson
# 2016-02-09

import os
import time
import glob
import psutil
import subprocess

import stump
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

stump.configure(logger)

motion_dir = '/tmp/motion'


@stump.ret('Determining picture filename', log=logging.DEBUG,
           postfix_only=True)
def name(pic):
    """Generate a name for the given picture."""
    return time.strftime("%Y-%m-%d %H:%M")


@stump.ret('Is process {name} running?', log=logging.DEBUG, postfix_only=True)
def process_running(name):
    """Returns True if named process is running."""
    return name in [i.name() for i in psutil.process_iter()]


@stump.put('Ensuring motion is running')
def ensure_motion_is_running():
    """Start motion if not running and give it a sec to boot up."""
    if not process_running('motion'):
        print('Starting motion')
        return subprocess.check_output('sudo motion'.split()).decode('utf-8')


@stump.put('Killing motion process')
def kill_motion():
    """Ensure the motion process is not active (blue webcam light off)."""
    if process_running('motion'):
        print('Stopping motion')
        return subprocess.check_output('sudo killall motion'.split()).decode('utf-8')


@stump.ret('Locating filenames in motion capture dir matching {pattern}',
           log=logging.DEBUG, postfix_only=True)
def motion_files(pattern='*'):
    return glob.glob(os.path.join(motion_dir, pattern))


if __name__ == '__main__':

    from notifiers.pushbulletnotifier import PushbulletNotifier
    handler = PushbulletNotifier('o.d6KVGP94jqzGR2arn8h4tPtnRNSggur1')

    from detectors.nmapdetector import nmapDetector
    sensor = nmapDetector('Erics-iPhone.att.net')

    while True:
        if not sensor.host_present:
            ensure_motion_is_running()  # TODO: background
            handler.notify(motion_files('*.jpg'))
            # Clean up motion_dir: discard swfs for room :: todo:
            # parametrize with handlers
            for swf in motion_files('*.swf'):
                os.remove(swf)
        else:
            kill_motion()
            for file in motion_files():
                os.remove(file)
            print('Eric is home -- sleeping')
        time.sleep(30)
