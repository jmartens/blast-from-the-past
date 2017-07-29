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

    align = openface.AlignDlib(args.dlibFacePredictor)
    net = openface.TorchNeuralNet(args.networkModel, imgDim=args.imgDim, cuda=args.cuda)

    logging.info('Discovering image files in: %s', path)
    for f in map(unicode, findimagesinfolder(path)):
        logging.info('Processing file: %s', f)
        logging.debug('TODO: Checking for file in database: %s', f)
        # If exists,
        # logging.debug('We have seen %s before, checking if it is modified', f)
        # logging.info('Skipping %s as it already exists and seems not to be modified', f)
        # If last_modified and size agree skip
        # logging.info('Skipping %s as after deep inspection it seems not to be modified', f)
        # If hash agrees skip
        # If not exists or changed (size, last modified date, hash?) process

        image = cv2.imread(f)
        if image is None:
            logging.error('Can not read file: %s', file)
        else:
            logging.info('Detecting faces...')
            faces = align.getAllFaceBoundingBoxes(image)
            cntFaces = len(faces)
            i = 0;
            for face in faces:
                i = i + 1;
                logging.debug('Face %d found at (%d, %d, %d, %d)', i, face.left(), face.top(), face.right(), face.bottom())
                logging.info('Processing face %d of %d', i, cntFaces)
                # TODO: store bounding box location in database and link to image
                # Process ROI for feeding it to the model
                logging.info('Aligning face %d of %d', i, cntFaces)
                alignedFace = align.align(
                    args.imgDim,
                    image,
                    face,
                    landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
                # Store processed ROI on filesystem
                phash = str(imagehash.phash(Image.fromarray(alignedFace)))
                logging.debug('Hashed face %d of %d is: %s', i, cntFaces, phash)
                hashedImage = os.path.join('/var/bftp/hashes', phash + '.jpg')
                cv2.imwrite(hashedImage, alignedFace)
                logging.debug('Saved face %d (%s) as %s', i, phash, hashedImage)
                # TODO: store processed ROI in database

            logging.info('Found %d faces in %s', i, f)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
