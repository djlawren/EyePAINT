"""
Feature Extraction
EyePAINT

By Dean Lawrence
"""

import cv2
import time

def weighted_average(previous_state, current_state, alpha):
    return [int(x[0] * (1 - alpha) + x[1] * alpha) for x in zip(previous_state, current_state)]

def get_largest_box(boxes):
    if len(boxes) == 0:
        return []
    
    largest = boxes[0]

    for (x, y, w, h) in boxes:
        if w * h > largest[2] * largest[3]:
            largest = (x, y, w, h)
    
    return largest

class FeatureExtraction():
    def __init__(self, face_cascade_path, eye_cascade_path):
        
        self.cap = cv2.VideoCapture(0)
        _, self.capture = self.cap.read()

        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        self.current_state = {
            "face": (0, 0, 10, 10),
            "right_eye": (0, 0, 10, 10),
            "left_eye": (0, 0, 10, 10),
            "right_pupil": (0, 0),
            "left_pupil": (0, 0)
        }

        self.calibration_data = []

        cv2.startWindowThread()

    def _detect_face(self, image, scale_factor=1.05, min_neighbors=6):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scale_factor, min_neighbors)
    
        return get_largest_box(faces)

    def _detect_eye(self, image, scale_factor=1.05, min_neighbors=6):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, scale_factor, min_neighbors)

        return get_largest_box(eyes)

    def _detect_pupil(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 0)
        _, _, min_loc, _ = cv2.minMaxLoc(gray)

        return min_loc

    def _capture_image(self):
        ret, self.capture = self.cap.read()
        
        if not ret:
            return -1
        else:
            return 1

    def _update_face_state(self, alpha):
        face = self._detect_face(self.capture)

        if len(face) == 0:
            return -1
        
        self.current_state["face"] = weighted_average(self.current_state["face"], face, alpha)

        return 1

    def _update_eye_state(self, alpha):
        face_x, face_y, face_w, face_h = self.current_state["face"]
        
        half_face_w = int(face_w / 2)
        half_face_h = int(face_h / 2)
        
        left_eye = self._detect_eye(self.capture[face_y:face_y+half_face_h, face_x:face_x+half_face_w])
        right_eye = self._detect_eye(self.capture[face_y:face_y+half_face_h, face_x+half_face_w:face_x+face_w])

        if len(left_eye) > 0:
            self.current_state["left_eye"] = weighted_average(self.current_state["left_eye"], (left_eye[0] + face_x, left_eye[1] + face_y, left_eye[2], left_eye[3]), alpha)

        if len(right_eye) > 0:
            self.current_state["right_eye"] = weighted_average(self.current_state["right_eye"], (right_eye[0] + face_x + half_face_w, right_eye[1] + face_y, right_eye[2], right_eye[3]), alpha)
        
        return 1

    def _update_pupil_state(self, alpha):
        left_eye_x, left_eye_y, left_eye_w, left_eye_h = self.current_state["left_eye"]
        right_eye_x, right_eye_y, right_eye_w, right_eye_h = self.current_state["right_eye"]

        left_pupil = self._detect_pupil(self.capture[left_eye_y:left_eye_y+left_eye_h, left_eye_x:left_eye_x+left_eye_w])
        right_pupil = self._detect_pupil(self.capture[right_eye_y:right_eye_y+right_eye_h, right_eye_x:right_eye_x+right_eye_w])

        left_tuple = tuple([sum(x) for x in zip((left_eye_x, left_eye_y), left_pupil)])
        right_tuple = tuple([sum(x) for x in zip((right_eye_x, right_eye_y), right_pupil)])

        self.current_state["left_pupil"] = weighted_average(self.current_state["left_pupil"], left_tuple, alpha)
        self.current_state["right_pupil"] = weighted_average(self.current_state["right_pupil"], right_tuple, alpha)
    
    def update_feature_state(self, face_alpha=0.15, eye_alpha=0.15, pupil_alpha=0.3):
        self._capture_image()
        
        self._update_face_state(face_alpha)
        self._update_eye_state(eye_alpha)
        self._update_pupil_state(pupil_alpha)

    def display_feature_state(self):
        img = self.capture

        face = self.current_state["face"]
        cv2.rectangle(img, (face[0], face[1]), (face[0]+face[2], face[1]+face[3]), (255, 0, 0), 2)
        
        right_eye = self.current_state["right_eye"]
        left_eye = self.current_state["left_eye"]
        cv2.rectangle(img, (right_eye[0], right_eye[1]), (right_eye[0]+right_eye[2], right_eye[1]+right_eye[3]), (0, 255, 0), 2)
        cv2.rectangle(img, (left_eye[0], left_eye[1]), (left_eye[0]+left_eye[2], left_eye[1]+left_eye[3]), (0, 255, 0), 2)
        
        cv2.circle(img, tuple(self.current_state["left_pupil"]), 5, (0, 0, 255), 2)
        cv2.circle(img, tuple(self.current_state["right_pupil"]), 5, (0, 0, 255), 2)

        cv2.imshow("img", img)
    
    def get_state_as_vector(self):
        temp_list = [self.current_state["face"], 
                     self.current_state["right_eye"], 
                     self.current_state["left_eye"], 
                     self.current_state["right_pupil"], 
                     self.current_state["left_pupil"]]
        
        final_list = []
        for lst in temp_list:
            for item in lst:
                final_list.append(item)

        return final_list
    
    def release(self):
        self.cap.release()
        for i in range(1,10):
            cv2.destroyAllWindows()
            cv2.waitKey(1)
