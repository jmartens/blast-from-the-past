import time
from watchdog.observers import Observer
import threading

# Database
from database import *
import peewee
from playhouse.db_url import connect
import os

# application setup
import argparse

# Face recognition
import openface

# File system monitoring
import FilesystemObserver
import FilesystemScanner
import FaceDetector

class MyThread(threading.Thread):

    def run(self):
        logging.debug('running')
        return

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s [%(threadName)s] %(name)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Setup openface
    logging.info('Parsing arguments')
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

    try:
        logging.info('Connecting to the database')
        logging.debug('Getting database parameters')
        database = os.environ.get('MYSQL_DATABASE') or 'bftp'
        user = os.environ.get('MYSQL_USER') or 'bftp'
        password = os.environ.get('MYSQL_PASSWORD') or 'bftp'
        host = os.environ.get('MYSQL_HOSTNAME') or 'db'
        port = os.environ.get('MYSQL_PORT') or 3306
        logging.debug('Connection string is mysql:///%s:%s@%s:%d/%s', user, password, host, port, database)
        db.init(database, user=user, password=password, host=host, port=port)

        create_my_tables()

        try:

            # Start file system scanner
            fsScanner = FilesystemScanner.FilesystemScanner()
            fsScanner.path = args.path
            fsScanner.start()

            while True:
                logging.debug('Sleeping for 1 second...')
                time.sleep(1)

        except KeyboardInterrupt:
            fsScanner.stop()
            db.close()

    except peewee.OperationalError:
        logging.error('There was an error connecting to the database, halting...')
