import cv2
import numpy
import time


class EyeDetector(object):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier("./data/haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier("./data/haarcascade_eye.xml")

    def get_faces(self, img):
        img = EyeDetector.convert_to_gray_scale(img)
        faces = self.face_cascade.detectMultiScale(img, 1.3, 5)
        if faces is None or len(faces) == 0:
            return []
        return faces

    def get_eyes(self, img):
        def pick_smaller_rect_if_clashes(eyes):
            print("pick_smaller_rect_if_clashes")
            ret = []
            selected_indices = []
            considered_indices = []
            for i, eye in enumerate(eyes):
                x, y, w, h = eye
                clashed_eyes = [[i,eye]]
                considered_indices.append(i)
                for j, e in enumerate(eyes):
                    if i == j:
                        continue
                    if x + w > e[0] and e[0] + e[2] > x:
                        clashed_eyes.append([j, e])
                smallest_w = 100000000
                smallest_x = 100000000
                chosen = None
                print(clashed_eyes)
                for j, e in clashed_eyes:
                    if smallest_w > e[2] or (smallest_w == e[2] and smallest_x < e[0]):
                        smallest_w = e[2]
                        smallest_x = e[0]
                        chosen = [j, e]
                if chosen is not None and chosen[0] not in selected_indices:
                    selected_indices.append(chosen[0])
                    ret.append(chosen[1])
                    print("chosen")
                    print(chosen)

            print("pick_smaller_rect_if_clashes done")
            return ret


        def pick_smaller_rect_if_clashes_improved(eyes):
            print("pick_smaller_rect_if_clashes")
            ret = []
            print("TTT")
            print(eyes)
            clashed_eyes_dict = {}
            for i, eye in enumerate(eyes):
                x, y, w, h = eye
                clashed_eyes = [[i,eye]]
                for j, e in enumerate(eyes):
                    if i == j:
                        continue
                    if x + w > e[0] and e[0] + e[2] > x:
                        clashed_eyes.append([j, e])
                print("AAA")
                print(clashed_eyes)
                clashed_eyes_dict[i] = clashed_eyes

            print(clashed_eyes_dict)
            for i, clashed_eyes in clashed_eyes_dict.items():
                smallest_w = 100000000
                smallest_x = 100000000
                chosen = None
                for j, e in clashed_eyes:
                    if smallest_w > e[2] > 30 or (smallest_w == e[2] and smallest_x < e[0]):
                        smallest_w = e[2]
                        smallest_x = e[0]
                        chosen = [j, e]
                if chosen is not None and chosen[0] == i:
                    ret.append(chosen[1])
                print("chosen")
                print(chosen)
            print("pick_smaller_rect_if_clashes done")
            return ret

        img = EyeDetector.convert_to_gray_scale(img)
        faces = self.get_faces(img)
        eyes = []
        for face in faces:
            # eyes.append([None, None])
            x, y, w, h = face
            gray_img_face_cut = img[y:y + h, x:x + w]
            eyes_in_this_face = self.eye_cascade.detectMultiScale(gray_img_face_cut)
            mid_face_h = w / 2
            mid_face_v = h / 2
            upper_eyes_in_this_face = []
            for e in eyes_in_this_face:
                # Eyes are on the upper part of a face.
                if e[1] > mid_face_v:
                    continue
                e[0] += x
                e[1] += y
                upper_eyes_in_this_face.append(e)
            print(upper_eyes_in_this_face)
            real_eyes_in_this_face = pick_smaller_rect_if_clashes_improved(upper_eyes_in_this_face)
            # eyes[-1][0] =
            eyes.append(real_eyes_in_this_face)
        return eyes

    @staticmethod
    def convert_to_gray_scale(img):
        if not isinstance(img, numpy.ndarray) or len(img.shape) > 2:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def load_img(filepath):
        return cv2.imread(filepath)


def main():
    eye_detector = EyeDetector()
    img = cv2.imread("./data/s1.jpg")
    print(eye_detector.get_eyes(img))
    # return
    # gray_picture = EyeDetector.get_gray_scale_img(img)
    # faces = eye_detector.get_eyes(gray_picture)[0]
    # print(faces)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(gray_picture, (x, y), (x + w, y + h), (255, 255, 0), 2)
    # cv2.imshow('my image', gray_picture)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("data/s.mp4")
    while True:
        _, frame = cap.read()
        eyes_in_faces = eye_detector.get_eyes(frame)
        if len(eyes_in_faces) > 0:
            eyes = eyes_in_faces[0]
        # for eyes in eye_detector.get_eyes(frame):
            # eyes = eye_detector.get_eyes(frame)[0]
            for (x, y, w, h) in eyes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.imshow('my image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(.1)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
