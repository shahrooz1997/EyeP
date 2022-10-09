#!/usr/bin/python3

import cv2
import time
import dlib
import notify2
import utils
import numpy
from imutils.video import VideoStream


class FaceDetectorCV(object):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier("./data/haarcascade_frontalface_default.xml")

    def get_faces(self, img):
        img = FaceDetectorCV.convert_to_gray_scale(img)
        faces = self.face_cascade.detectMultiScale(img, 1.3, 5)
        if faces is None or len(faces) == 0:
            return []
        return faces

    @staticmethod
    def convert_to_gray_scale(img):
        if not isinstance(img, numpy.ndarray) or len(img.shape) > 2:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def load_img(filepath):
        return cv2.imread(filepath)


class EyeDetector(object):
    EAR_THRESHOLD = 0.25

    def __init__(self):
        self.cv_helper = FaceDetectorCV()
        self.face_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")

    def get_faces(self, img):
        return self.face_detector(img, 1)
        # faces = self.cv_helper.get_faces(img)
        # if len(faces) == 0 or len(faces) >= 2:
        #     print("No using CV")
        #     cv2.imshow('my image', img)
        #     return self.face_detector(img, 1)
        #
        # print("using CV")
        # x, y, w, h = faces[0]
        # img = img[y-100:y + h + 100, x-50:x + w + 50]
        # faces = self.face_detector(img, 1)
        # cv2.rectangle(img, (50, 100), (50 + w, 100 + h), (255, 255, 0), 2)
        # cv2.imshow('my image', img)
        # # time.sleep(5)
        # # print("Number of faces detected: {}".format(len(faces)))
        # return faces

    def get_eyes(self, img):
        def get_eye_parts(shape):
            return [[shape.part(36), shape.part(37), shape.part(38), shape.part(39), shape.part(40), shape.part(41)],
                    [shape.part(42), shape.part(43), shape.part(44), shape.part(45), shape.part(46), shape.part(47)]]

        faces = self.get_faces(img)
        ret = []
        for f in faces:
            shape = self.predictor(img, f)
            ret.append(get_eye_parts(shape))

        return ret

    @staticmethod
    def is_eye_closed(eye):
        def compute_ear(eye):
            return (utils.compute_distance(eye[1], eye[5]) + utils.compute_distance(eye[2], eye[4])) / (
                    2 * utils.compute_distance(eye[0], eye[3]))

        if compute_ear(eye) < EyeDetector.EAR_THRESHOLD:
            return True
        return False

    @staticmethod
    def load_img(filepath):
        return dlib.load_rgb_image(filepath)
        # return cv2.imread(filepath)


class Handler:
    APPLICATION_NAME = "EyeP"
    RESOLUTION = (640, 480)

    def __init__(self, src=0):
        notify2.init(Handler.APPLICATION_NAME)
        self.eye_detector = EyeDetector()
        # # self.cap = cv2.VideoCapture("data/s.mp4")
        # self.cap = cv2.VideoCapture(src)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.set(cv2.CAP_PROP_FPS, 5)

        self.src = src
        self.vs = VideoStream(self.src, resolution=Handler.RESOLUTION).start()

    def run(self, video_output=False):
        # while True:
        #     t = time.time()
        #     img = self.vs.read()
        #     print("SSSS {}", time.time() - t)

        counter = -1
        time_when_closed = time.time()
        notice = None
        closed_eye = False
        time_when_notified = time.time()
        time_when_eyes_detected = time.time()
        time_when_blinked = None
        blink_number = 0
        while True:
            img = self.vs.read()
            # _, img = self.cap.read()
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if img is None:
                break
            counter = (counter + 1) % 2
            if counter != 0:
                time.sleep(.01)
                continue
            eyes_in_faces = self.eye_detector.get_eyes(img)
            if len(eyes_in_faces) > 0:
                time_when_eyes_detected = time.time()
                eyes = eyes_in_faces[0]
                # print(eyes)
                last_closed_eye = closed_eye
                closed_eye = self.eye_detector.is_eye_closed(eyes[0]) or self.eye_detector.is_eye_closed(eyes[1])
                if closed_eye:
                    time_when_closed = time.time()
                    if notice is not None:
                        notice.close()
                if last_closed_eye and not closed_eye:
                    if time_when_blinked is None or time.time() - time_when_blinked > 3:
                        if time_when_blinked is not None:
                            print("Blinked {} after {}s".format(blink_number, time.time() - time_when_blinked))
                        time_when_blinked = time.time()
                        blink_number += 1
                if video_output:
                    for e in eyes:
                        for point in e:
                            cv2.circle(img, (point.x, point.y), 1, color=(0, 255, 255))
                    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            else:
                time_when_closed = time.time()
                time_when_blinked = None
                if notice is not None:
                    notice.close()
                print("No eyes detected for {}s".format(time.time() - time_when_eyes_detected))
            if video_output:
                cv2.imshow('my image', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time_since_closed = time.time() - time_when_closed
            if time_since_closed > 10 and time.time() - time_when_notified > 5:
                if notice is not None:
                    notice.close()
                notice = notify2.Notification("EyeP",
                                              "You didn't blink for more than {} seconds".format(time_since_closed))
                notice.show()
                time_when_notified = time.time()
            if time.time() - time_when_eyes_detected > 3*60:
                print("No eyes are detected for 3 mins; sleeping for 15 mins")
                self.vs.stop()
                self.vs.stream.release()
                time.sleep(15*60)
                self.vs = VideoStream(self.src, resolution=Handler.RESOLUTION).start()
                time_when_eyes_detected = time.time()


def main():
    handler = Handler(src=0)
    handler.run(video_output=True)


if __name__ == '__main__':
    main()
