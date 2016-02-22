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


@stump.put("Executing command: '{command}'", log=logging.DEBUG)
def shell_output(command):
    """Return stdout of specified command in shell."""
    return subprocess.check_output(command.split()).decode('utf-8')


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
        return shell_output('sudo motion')


@stump.put('Killing motion process')
def kill_motion():
    """Ensure the motion process is not active (blue webcam light off)."""
    if process_running('motion'):
        return shell_output('sudo killall motion')


@stump.ret('Locating filenames in motion capture dir matching {pattern}',
           log=logging.DEBUG, postfix_only=True)
def motion_files(pattern='*'):
    return glob.glob(os.path.join(motion_dir, pattern))


def main():
    # TODO: parse args including api key and target
    # TODO: parse from config file if args not found

    api_key = 'o.d6KVGP94jqzGR2arn8h4tPtnRNSggur1'
    target = 'Erics-iPhone.att.net'

    from notifiers.pushbulletnotifier import PushbulletNotifier
    handler = PushbulletNotifier(api_key)

    from detectors.nmapdetector import nmapDetector
    sensor = nmapDetector(target)

    while True:
        if not sensor.host_present:
            ensure_motion_is_running()
            handler.notify(motion_files('*.jpg'))
            for swf in motion_files('*.swf'):
                handler.archive(swf)
        else:
            logger.debug('%s is home -- sleeping', user())
            kill_motion()
            for file in motion_files():
                try:
                  os.remove(file)
                except:
                    pass
        time.sleep(30)


if __name__ == '__main__':
    main()
