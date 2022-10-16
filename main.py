#!/usr/bin/python3

import os
import cv2
import time
import dlib
from utils import *
from imutils.video import VideoStream
import argparse

if is_linux_based():
    import notify2
else:
    import pynotifier

APPLICATION_NAME = "EyeP"
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


class EyeDetector(object):
    EAR_THRESHOLD = 0.25

    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(os.path.join(SCRIPT_PATH, "data/shape_predictor_68_face_landmarks.dat"))

    def get_faces(self, img):
        return self.face_detector(img, 1)

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
            return (compute_distance(eye[1], eye[5]) + compute_distance(eye[2], eye[4])) / (
                    2 * compute_distance(eye[0], eye[3]))

        if compute_ear(eye) < EyeDetector.EAR_THRESHOLD:
            return True
        return False

    @staticmethod
    def load_img(filepath):
        return dlib.load_rgb_image(filepath)
        # return cv2.imread(filepath)


class Notification:
    if is_linux_based():
        notify2.init(APPLICATION_NAME)

    def __init__(self, message):
        if is_linux_based():
            self.notif = notify2.Notification(APPLICATION_NAME, message)
        else:
            if is_linux_based():
                icon_path = os.path.join(SCRIPT_PATH, "icon.png")
            else:
                icon_path = os.path.join(SCRIPT_PATH, "icon.ico")
            self.notif = pynotifier.Notification(
                title=APPLICATION_NAME,
                description=message,
                icon_path=icon_path,
                duration=5,
                urgency='normal'
            )

    def show(self):
        if is_linux_based():
            self.notif.show()
        else:
            self.notif.send()

    def close(self):
        if is_linux_based():
            self.notif.close()
        else:
            pass


class Handler:
    RESOLUTION = (640, 480)

    def __init__(self, src=0, output_video=False):
        self.eye_detector = EyeDetector()
        self.src = src
        self.output_video = output_video
        self.vs = VideoStream(self.src, resolution=Handler.RESOLUTION).start()

    def run(self):
        counter = -1
        time_when_closed = time.time()
        notif = None
        closed_eye = False
        time_when_notified = time.time()
        time_when_eyes_detected = time.time()
        no_eyes_detected = False
        time_when_blinked = None
        blink_number = 0
        while True:
            img = self.vs.read()
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
                no_eyes_detected = False
                eyes = eyes_in_faces[0]
                # print(eyes)
                last_closed_eye = closed_eye
                closed_eye = self.eye_detector.is_eye_closed(eyes[0]) or self.eye_detector.is_eye_closed(eyes[1])
                if closed_eye:
                    time_when_closed = time.time()
                    if notif is not None:
                        notif.close()
                if last_closed_eye and not closed_eye:
                    if time_when_blinked is None or time.time() - time_when_blinked > 3:
                        if time_when_blinked is not None:
                            print("Blinked {} after {}s".format(blink_number, time.time() - time_when_blinked))
                        time_when_blinked = time.time()
                        blink_number += 1
                if self.output_video:
                    for e in eyes:
                        for point in e:
                            cv2.circle(img, (point.x, point.y), 1, color=(0, 255, 255))
                    # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            else:
                time_when_closed = time.time()
                time_when_blinked = None
                if notif is not None:
                    notif.close()
                print("No eyes detected for {}s".format(time.time() - time_when_eyes_detected))
            if self.output_video:
                cv2.imshow('my image', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            time_since_closed = time.time() - time_when_closed
            if time_since_closed > 10 and time.time() - time_when_notified > 5:
                if notif is not None:
                    notif.close()
                notif = Notification("You didn't blink for more than {} seconds".format(time_since_closed))
                notif.show()
                time_when_notified = time.time()
            if time.time() - time_when_eyes_detected > 3 * 60 or (
                    no_eyes_detected and time.time() - time_when_eyes_detected > 60):
                if no_eyes_detected:
                    print("No eyes are detected for 1 mins; sleeping for 15 mins")
                else:
                    print("No eyes are detected for 3 mins; sleeping for 15 mins")
                no_eyes_detected = True
                self.vs.stop()
                self.vs.stream.release()
                time.sleep(15 * 60)
                self.vs = VideoStream(self.src, resolution=Handler.RESOLUTION).start()
                time_when_eyes_detected = time.time()


def parse_args():
    parser = argparse.ArgumentParser(description="This app helps you to protect your eyes while using a computer")
    parser.add_argument("-s", "--source",
                        default=0,
                        type=int,
                        help="The source of video input (default: 0)")
    parser.add_argument("-o", "--output_video",
                        action="store_true",
                        help="Whether to show the input video; it could be useful to set up your webcam "
                             "(default: False)")
    parser.add_argument("-r", "--resolution",
                        nargs=2,
                        type=int,
                        default=(640, 480),
                        metavar=('WIDTH', 'HEIGHT'),
                        help="The resolution to use to read the input video (default: (640, 480))")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    handler = Handler(src=args.source, output_video=args.output_video)
    handler.run()


if __name__ == '__main__':
    main()
