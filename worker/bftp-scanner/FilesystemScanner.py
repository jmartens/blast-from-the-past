from threading import Thread
import logging

import os
import datetime

from database import Image, Queue

# Listing files
import glob
import re

import cv2
import imagehash
from PIL import Image as PILImage

try:
    from os import scandir
except ImportError:
    # use scandir PyPI module on Python < 3.5
    from scandir import scandir


def scantree(directory):
    """Recursively yield DirEntry objects for given directory."""
    list = scandir(directory)
    try:
        for entry in list:
            if entry.is_dir(follow_symlinks=False):
                for entry in scantree(entry.path):
                    yield entry
            else:
                yield entry
    except OSError:
        logging.info('Failed to access')
        pass
    except UnicodeDecodeError:
        logging.info('Illegal filename')
        pass
    else:
        logging.info('Other error')
        pass


class FilesystemScanner(Thread):

    def findimagesinfolder(self, pattern=('.jpg', '*.jpeg', '.png', '.bmp')):

        if not os.path.exists(self.path):
            raise ValueError("Directory not found {}".format(self.path))

        matches = []
        logging.info('Start discovering items in %s', self.path)
        for entry in scantree(self.path):
            if entry.name.lower().endswith(pattern):
                matches.append(entry)
        logging.info('Finished discovering items in %s', self.path)
        return matches

    def run(self):
        self.name = __name__
        logging.info('Discovering image files in: %s', self.path)
        for entry in self.findimagesinfolder():
            file = entry.path
            logging.info('Processing file: %s', file)

            logging.debug('Reading file: %s', file)
            image = cv2.imread(file)
            if image is None:
                logging.error('Skipping: unable to read file: %s', file)
                continue

            logging.debug('Checking against %s against database', file)
            record, created = Image.get_or_create(
                path=os.path.dirname(file),
                name=os.path.basename(file),
                size=os.path.getsize(file),
                created=datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime('%Y-%m-%d %H:%M:%S'),
                modified=datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S'),
                hash=str(imagehash.phash(PILImage.fromarray(image))))

            if created:
                logging.info('Adding %s to the queue as it seems to be new', file)
                Queue.create(image=record.id)
            else:
                logging.debug('We have seen %s before, checking if it is modified', file)
                # TODO: find out why date comparison like below keeps evaluating to False while values seem to be equal
                # (record.modified == datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime(
                #     '%Y-%m-%d %H:%M:%S')) & \
                # (record.created == datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime(
                #     '%Y-%m-%d %H:%M:%S')) & \
                if (os.path.getsize(file) == record.size) & \
                        (record.hash == str(imagehash.phash(PILImage.fromarray(image)))):
                    logging.info('Skipping %s as it already exists and seems not to be modified', file)
                    continue
                else:
                    logging.info('Adding %s to the queue as it seems to have changed', file)
                    Queue.create(image=record.id)

        return

