import cv2
import time
import dlib
import notify2
import utils


class EyeDetector(object):
    EAR_THRESHOLD = 0.19

    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")

    def get_faces(self, img):
        faces = self.face_detector(img, 1)
        # print("Number of faces detected: {}".format(len(faces)))
        return faces

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

    def __init__(self):
        notify2.init(Handler.APPLICATION_NAME)
        self.eye_detector = EyeDetector()

    def run(self):
        cap = cv2.VideoCapture("data/s.mp4")
        counter = -1
        time_when_blinked = time.time()
        notice = None
        time_when_notified = time.time()
        while True:
            _, frame = cap.read()
            if frame is None:
                break
            counter = (counter + 1) % 10
            if counter != 0:
                continue
            eyes_in_faces = self.eye_detector.get_eyes(frame)
            if len(eyes_in_faces) > 0:
                eyes = eyes_in_faces[0]
                # print(eyes)
                if self.eye_detector.is_eye_closed(eyes[0]) or self.eye_detector.is_eye_closed(eyes[1]):
                    print("Blinked")
                    time_when_blinked = time.time()
                    if notice is not None:
                        notice.close()
                # for e in eyes:
                #     for point in e:
                #         cv2.circle(frame, (point.x, point.y), 3, color=(0, 255, 255))
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.imshow('my image', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time_since_blinked = time.time() - time_when_blinked
            if time_since_blinked > 10 and time.time() - time_when_notified > 5:
                if notice is not None:
                    notice.close()
                notice = notify2.Notification("EyeP",
                                              "You didn't blink for more than {} seconds".format(time_since_blinked))
                notice.show()
                time_when_notified = time.time()


def main():
    handler = Handler()
    handler.run()


if __name__ == '__main__':
    main()
