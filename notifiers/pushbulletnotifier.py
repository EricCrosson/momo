#!/usr/bin/env python
# Written by Eric Crosson
# 2016-02-16

from notifiers.notifier import Notifier
from pushbullet import Pushbullet

import stump
import logging
import subprocess

# TODO: document


class PushbulletNotifier(Notifier):


    def __init__(self, api_key, archive='/dev/null', **kwargs):
        self.pb = Pushbullet(api_key)
        self.archive = archive


    @stump.put("Executing command: '{command}'", log=logging.DEBUG)
    def shell_output(self, command):
        """Return stdout of specified command in shell."""
        return subprocess.check_output(command.split()).decode('utf-8')


    @stump.put('Notifying user of {files}')
    def notify(self, files):
        """Notify connected user of files."""
        for file in files:
            with open(file, 'rb') as pic:
                file_data = self.pb.upload_file(pic, name(pic))
                push = self.pb.push_file(**file_data)
            self.archive(file)


    @stump.put('Archiving {file}')
    def archive(self, file):
        """Archive file in specified archive dir."""
        # TODO: differentiate between video files from motion (swf, any
        # others?) and output jpgs (any others?) and handle them appropriately
        shell_output('cp {file} {target}'.format(file=file,
                                                 target=self.archive).split())
