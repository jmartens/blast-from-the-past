import time
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

    # Setup openface
    fileDir = '/root/openface/demos/'
    modelDir = os.path.join(fileDir, '..', 'models')
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')

    parser = argparse.ArgumentParser()
    parser.add_argument('--dlibFacePredictor', type=str, help="Path to dlib's face predictor.",
                        default=os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
    parser.add_argument('--networkModel', type=str, help="Path to Torch network model.",
                        default=os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'))
    parser.add_argument('--imgDim', type=int,
                        help="Default image dimension.", default=96)
    parser.add_argument('--cuda', action='store_true')
    parser.add_argument('--unknown', type=bool, default=False,
                        help='Try to predict unknown people')
    #    parser.add_argument('--port', type=int, default=9000,
    #                        help='WebSocket Port')
    parser.add_argument('--path', type=str, default='.',
                        help='Specify image search path')

    args = parser.parse_args()

    path = args.path;

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
