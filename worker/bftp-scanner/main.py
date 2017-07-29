import time
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

# Listing files
import os
import glob
import re

# application setup
import argparse

# Face recognition
import openface
import cv2
import imagehash
from PIL import Image

class MyEventHandler(LoggingEventHandler):

    def on_moved(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)


def findfiletypesinfolder(path, pattern):
    logging.debug("Finding image files in %s", path)
    files = filter(pattern.match, glob.glob(os.path.join(path, '*/*')))
    logging.debug("Found %d images in %s", len(files), path)
    return files


def findimagesinfolder(path):
    pattern = r'(.*\.(?:jpe?g|png|bmp))'
    r = re.compile(pattern, re.IGNORECASE)
    return findfiletypesinfolder(path, r)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
