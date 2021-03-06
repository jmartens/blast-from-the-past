from threading import Thread
import logging

import os
import datetime

from database import ROI, Image, Object, Queue

import cv2
import imagehash
from PIL import Image as PILImage
import openface


class FaceDetector(Thread):

    def run(self):
        self.name = __name__
        logging.info('Detecting faces...')
        start = datetime.datetime.now()
        for file in Image.select().join(Queue).where(Queue.status==None):

            logging.info('Processing file %s', os.path.join(file.path, file.name))
            logging.debug('Reading file %s', os.path.join(file.path, file.name))
            image = cv2.imread(os.path.join(file.path, file.name))

            logging.debug('Detecting faces')
            faces = self.align.getAllFaceBoundingBoxes(image)
            numberOfFaces = len(faces)

            q = Queue.get(image=file.id)

            if numberOfFaces > 0:

                logging.info('Detected faces: %d', numberOfFaces)
                i = 0

                logging.info('Processing detected faces')
                for face in faces:
                    i = i + 1;
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

                q.status = 1

            else:
                logging.info('No faces detected')
                q.status = 1

            logging.debug('Updating status to failed (%d)', q.status)
            q.save()

        return
