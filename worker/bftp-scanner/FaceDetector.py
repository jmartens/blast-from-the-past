from threading import Thread
import logging

import os
import datetime
import peewee

from database2 import ROI, Image, Subject as Object, Queue

import cv2
import imagehash
from PIL import Image as PILImage
import openface


class FaceDetector(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.failurecount = 0
        self.name = __name__

    def run(self):
        logging.info('Detecting faces...')
        start = datetime.datetime.now()
        while True:
            try:
                logging.debug('Retieving item from queue')
                q = (Queue.select().join(Image).where(Queue.status == None).order_by(Queue.priority.desc(), Queue.id)).get()

                logging.debug('Setting queue item %s to processing (1)', q.id)
                q.status = 1
                q.save()

                logging.debug('Resetting failure counter')
                self.failurecount = 0

                logging.debug('Retrieving file with id %d', q.image.id)
                file = q.image

                logging.info('Processing file %s', os.path.join(file.path, file.name))
                logging.debug('Reading file %s', os.path.join(file.path, file.name))
                image = cv2.imread(os.path.join(file.path, file.name))

                logging.debug('Detecting faces')
                faces = self.align.getAllFaceBoundingBoxes(image)
                numberOfFaces = len(faces)

                if numberOfFaces > 0:

                    logging.info('Detected faces: %d', numberOfFaces)
                    i = 0

                    logging.info('Processing detected faces')
                    for face in faces:
                        i = i + 1
                        logging.info('Processing face %d of %d at (%d, %d, %d, %d)',
                                      i,
                                      numberOfFaces,
                                      face.left(),
                                      face.top(),
                                      face.right(),
                                      face.bottom())
                        logging.debug('Store bounding box location in database and link to image');
                        roirec = ROI.create(image=file.id,
                                            left=face.left(),
                                            top=face.top(),
                                            bottom=face.bottom(),
                                            right=face.right())

                        # Process ROI for feeding it to the model
                        logging.debug('Aligning face for model training')
                        alignedFace = self.align.align(
                            self.imgDim,
                            image,
                            face,
                            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)

                        # Store processed ROI on filesystem
                        phash = str(imagehash.phash(PILImage.fromarray(alignedFace)))
                        logging.debug('Hashed face: %s', phash)
                        hashedImage = os.path.join('/var/bftp/hashes', phash + '.jpg')
                        cv2.imwrite(hashedImage, alignedFace)
                        Object.create(roi=roirec.id,
                                      hash=phash,
                                      path=hashedImage,
                                      userid=None)
                        logging.debug('Saved face as %s', hashedImage)

                    q.status = numberOfFaces

                else:
                    logging.info('No faces detected')
                    q.status = 0

                logging.debug('Updating status to %d', q.status)
                q.save()
            except peewee.DoesNotExist:
                logging.error('Unable to access queue.')
                self.failurecount += 1
                logging.debug('Setting failure count to %d', self.failurecount)

            logging.debug('Processing took %0   .2d seconds', (datetime.datetime.now() - start).total_seconds()/1000)

        return
