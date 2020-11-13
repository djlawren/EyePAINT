

import math
import cv2
import dlib
import numpy as np
import time
import mtcnn

def weighted_average(previous_state, current_state, alpha):
    """
    Computes an elementwise weighted average between two arrays
    """

    return [int(x[0] * (1 - alpha) + x[1] * alpha) for x in zip(previous_state, current_state)]

def get_largest_box(boxes):
    """
    Given a list of bounding boxes, returns the box with the greatest area
    """

    if len(boxes) == 0:
        return []
    
    largest = boxes[0]

    for (x, y, w, h) in boxes:
        if w * h > largest[2] * largest[3]:
            largest = (x, y, w, h)
    
    return largest

def box_to_rect(box):
    """
    Converts box in (x,y,w,h) format into dlib rectangle object
    """

    return dlib.rectangle(box[0], box[1], box[0]+box[2], box[1]+box[3])

def rect_to_box(rect):
    """
    Converts dlib rectangle object into (x,y,w,h) tuple for bounding box
    """

    return (rect.left(), rect.top(), rect.width(), rect.height())

def convert_shape_to_list(shape):
    """
    Converts dlib shape object to list
    """

    lst = []
    for i in range(0, 68):
        lst.append(shape.part(i).x)
        lst.append(shape.part(i).y)
    
    return lst

def get_point_from_shapelist(shapelist, index):
    """
    Given a list created from a pose shape and point number, return an (x,y) tuple
    """

    return (shapelist[index * 2], shapelist[index * 2 + 1])

def get_x_gradient(image):
    output = np.zeros(image.shape, dtype=np.double)
    for y in range(0, len(image)):
        output[y][0] = image[y][1] - image[y][0]
        for x in range(1, len(image[y]) - 1):
            output[y][x] = (image[y][x+1] - image[y][x-1]) / 2.0
        output[y][-1] = image[y][-1] - image[y][-2]
    
    return output

def get_image_gradients(image):

    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3).astype('float64')
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3).astype('float64')

    #sobel_x = get_x_gradient(image)
    #sobel_y = np.transpose(get_x_gradient(np.transpose(image)))

    return sobel_x, sobel_y

def get_magnitudes(x_gradients, y_gradients):
    mags = np.zeros(x_gradients.shape, dtype=np.double)
    for y in range(0, len(mags)):
        for x in range(0, len(mags[y])):
            mags[y][x] = math.sqrt((x_gradients[y][x] * x_gradients[y][x]) + (y_gradients[y][x] * y_gradients[y][x]))
    
    return mags

def compute_threshold(image, std_dev_factor):
    mean = np.mean(image)
    std_dev = np.std(image)

    return std_dev_factor * std_dev + mean

def normalize_gradients(x_gradients, y_gradients, magnitudes, threshold):
    for y in range(0, len(x_gradients)):
        for x in range(0, len(x_gradients[y])):
            if magnitudes[y][x] > threshold:
                #print(x_gradients[y][x])
                x_gradients[y][x] /= magnitudes[y][x] * 1.0
                #print(x_gradients[y][x])
                y_gradients[y][x] /= magnitudes[y][x] * 1.0
            else:
                x_gradients[y][x] = 0
                y_gradients[y][x] = 0

def blur_and_invert(image):
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    for y in range(0, len(blurred)):
        for x in range(0, len(blurred[y])):
            blurred[y][x] = 255 - blurred[y][x]
    
    return blurred

def test_center(x, y, weights, gx, gy, output):
    for cy in range(0, len(output)):
        for cx in range(0, len(output[cy])):
            if x == cx and y == cy:
                continue

            dx = x - cx
            dy = y - cy

            magnitude = math.sqrt((dx * dx) + (dy * dy))

            dx /= magnitude
            dy /= magnitude

            dot = max(0, dx * gx + dy * gy)

            output[cy][cx] += dot * dot * (weights[y][x] / 0.1)

def test_all_centers(image, weights, x_gradients, y_gradients):
    output = np.zeros(image.shape, dtype=np.double)
    for y in range(0, len(image)):
        for x in range(0, len(image[y])):
            if x_gradients[y][x] == 0 and y_gradients[y][x] == 0:
                continue

            test_center(x, y, weights, x_gradients[y][x], y_gradients[y][x], output)
    
    return output

def scale_image(image, width):
    return cv2.resize(image, (width, width), interpolation=cv2.INTER_AREA)

def unscale_point(point, factor):
    pass

class FeatureExtraction():
    def __init__(self, face_cascade_path, eye_cascade_path, shape_predictor_path):
        
        self.cap = cv2.VideoCapture(0)
        _, self.capture = self.cap.read()

        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        self.pose_predictor = dlib.shape_predictor(shape_predictor_path)
        self.mtcnn_detector = mtcnn.MTCNN()
        self.hog_detector = dlib.get_frontal_face_detector()

        self.current_state = {
            "face": (0, 0, 100, 100),
            "right_eye": (0, 0, 10, 10),
            "left_eye": (0, 0, 10, 10),
            "right_pupil": (0, 0),
            "left_pupil": (0, 0),
            "pose": [0 for i in range(0, 68 * 2)]
        }

        cv2.startWindowThread()

    def _detect_face_haar(self, image, scale_factor=1.05, min_neighbors=6):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scale_factor, min_neighbors)
    
        return get_largest_box(faces)

    def _detect_face_hog(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = self.hog_detector(gray, 0)
        faces = [rect_to_box(rect) for rect in rects]

        return get_largest_box(faces)

    def _detect_face_mtcnn(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = [i['box'] for i in self.mtcnn_detector.detect_faces(rgb)]

        return get_largest_box(faces)

    def _detect_eye_haar(self, image, scale_factor=1.05, min_neighbors=6):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, scale_factor, min_neighbors)

        return get_largest_box(eyes)

    def _detect_pose(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rect = box_to_rect(self.current_state["face"])

        return convert_shape_to_list(self.pose_predictor(gray, rect))

    def _detect_pupil(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        _, _, min_loc, _ = cv2.minMaxLoc(gray)

        return min_loc
    
    def _detect_pupil_dot(self, image, image_scale=20):
        
        width_scale = image.shape[1] / image_scale
        height_scale = image.shape[1] / image_scale

        print(width_scale, height_scale)

        #blurred = cv2.GaussianBlur(image, (5, 5), 0)
        downscaled = scale_image(image, image_scale)

        gray = cv2.cvtColor(downscaled, cv2.COLOR_BGR2GRAY)

        x_gradients, y_gradients = get_image_gradients(gray)    # Compute gradients in each direction as well as magnitude
        magnitudes = get_magnitudes(x_gradients, y_gradients)

        #cv2.imshow("magnitudes", magnitudes)

        threshold = compute_threshold(magnitudes, 2)   # compute the threshold for culling the gradients

        normalize_gradients(x_gradients, y_gradients, magnitudes, threshold)    # Normalize and cull gradients

        print(threshold)
        #print(x_gradients)

        weights = blur_and_invert(gray) # Find weights by blurring and inverting the image

        possible = test_all_centers(gray, weights, x_gradients, y_gradients)    # get a matrix of possible centers
        
        _, _, _, max_loc = cv2.minMaxLoc(possible)  # Find the max of that centers matrix as the eye center

        return (int(max_loc[0] * width_scale), int(max_loc[1] * height_scale))

    def _capture_image(self):
        ret, self.capture = self.cap.read()
        
        if not ret:
            return -1
        else:
            return 1

    def _update_face_state(self, alpha):
        face = self._detect_face_hog(self.capture)

        if len(face) == 0:
            return -1
        
        self.current_state["face"] = weighted_average(self.current_state["face"], face, alpha)

        return 1

    def _update_eye_state(self, alpha):
        face_x, face_y, face_w, face_h = self.current_state["face"]
        
        half_face_w = int(face_w / 2)
        half_face_h = int(face_h / 2)
        
        left_eye = self._detect_eye_haar(self.capture[face_y:face_y+half_face_h, face_x:face_x+half_face_w])
        right_eye = self._detect_eye_haar(self.capture[face_y:face_y+half_face_h, face_x+half_face_w:face_x+face_w])

        if len(left_eye) > 0:
            self.current_state["left_eye"] = weighted_average(self.current_state["left_eye"], (left_eye[0] + face_x, left_eye[1] + face_y, left_eye[2], left_eye[3]), alpha)

        if len(right_eye) > 0:
            self.current_state["right_eye"] = weighted_average(self.current_state["right_eye"], (right_eye[0] + face_x + half_face_w, right_eye[1] + face_y, right_eye[2], right_eye[3]), alpha)
        
        return 1
    
    def _update_eye_state_from_pose(self, alpha):
        if len(self.current_state['pose']) == 0:
            return -1
        
        left_outer_point = get_point_from_shapelist(self.current_state['pose'], 36)
        left_inner_point = get_point_from_shapelist(self.current_state['pose'], 39)

        right_outer_point = get_point_from_shapelist(self.current_state['pose'], 45)
        right_inner_point = get_point_from_shapelist(self.current_state['pose'], 42)

        left_width = left_inner_point[0] - left_outer_point[0]
        right_width = right_outer_point[0] - right_inner_point[0]

        left_x = left_outer_point[0]
        right_x = right_inner_point[0]
        left_y = left_outer_point[1] - left_width / 2
        right_y = right_inner_point[1] - right_width / 2

        left_eye = (left_x, left_y, left_width, left_width)
        right_eye = (right_x, right_y, right_width, right_width)

        self.current_state["left_eye"] = weighted_average(self.current_state["left_eye"], left_eye, alpha)
        self.current_state["right_eye"] = weighted_average(self.current_state["right_eye"], right_eye, alpha)

        return 1
    
    def _update_pose_state(self, alpha):
        detected_pose = self._detect_pose(self.capture)

        for i in [x for x in range(68 * 2) if x % 2 == 0]:
            detected_pose[i] -= self.current_state["face"][0]
            detected_pose[i + 1] -= self.current_state["face"][1]
        
        self.current_state["pose"] = weighted_average(self.current_state["pose"], detected_pose, alpha)
        #self.current_state["pose"] = self._detect_pose(self.capture)

        return 1

    def _update_pupil_state(self, alpha):
        left_eye_x, left_eye_y, left_eye_w, left_eye_h = self.current_state["left_eye"]
        right_eye_x, right_eye_y, right_eye_w, right_eye_h = self.current_state["right_eye"]
        face_x, face_y, _, _ = self.current_state["face"]

        left_eye_x += face_x
        left_eye_y += face_y
        right_eye_x += face_x
        right_eye_y += face_y

        left_pupil = self._detect_pupil_dot(self.capture[left_eye_y:left_eye_y+left_eye_h, left_eye_x:left_eye_x+left_eye_w])
        right_pupil = self._detect_pupil_dot(self.capture[right_eye_y:right_eye_y+right_eye_h, right_eye_x:right_eye_x+right_eye_w])

        #left_tuple = tuple([sum(x) for x in zip((left_eye_x, left_eye_y), left_pupil)])
        #right_tuple = tuple([sum(x) for x in zip((right_eye_x, right_eye_y), right_pupil)])

        self.current_state["left_pupil"] = weighted_average(self.current_state["left_pupil"], left_pupil, alpha)
        self.current_state["right_pupil"] = weighted_average(self.current_state["right_pupil"], right_pupil, alpha)

        return 1
    
    def update_feature_state(self, face_alpha=0.15, eye_alpha=1, pupil_alpha=0.3, pose_alpha=0.7):
        self._capture_image()
        
        self._update_face_state(face_alpha)
        self._update_pose_state(pose_alpha)
        #self._update_eye_state(eye_alpha)
        self._update_eye_state_from_pose(eye_alpha)
        self._update_pupil_state(pupil_alpha)
        

    def display_feature_state(self):
        img = self.capture

        face = self.current_state["face"]
        cv2.rectangle(img, (face[0], face[1]), (face[0]+face[2], face[1]+face[3]), (255, 0, 0), 2)
        
        right_eye = self.current_state["right_eye"]
        left_eye = self.current_state["left_eye"]
        cv2.rectangle(img, (right_eye[0]+face[0], right_eye[1]+face[1]), (right_eye[0]+right_eye[2]+face[0], right_eye[1]+right_eye[3]+face[1]), (0, 255, 0), 2)
        cv2.rectangle(img, (left_eye[0]+face[0], left_eye[1]+face[1]), (left_eye[0]+left_eye[2]+face[0], left_eye[1]+left_eye[3]+face[1]), (0, 255, 0), 2)
        
        left_tuple = tuple([sum(x) for x in zip((left_eye[0]+face[0], left_eye[1]+face[1]), self.current_state["left_pupil"])])
        right_tuple = tuple([sum(x) for x in zip((right_eye[0]+face[0], right_eye[1]+face[1]), self.current_state["right_pupil"])])

        cv2.circle(img, left_tuple, 5, (0, 0, 255), 2)
        cv2.circle(img, right_tuple, 5, (0, 0, 255), 2)

        for point in range(0, 68):
            initial_point = list(get_point_from_shapelist(self.current_state['pose'], point))
            initial_point[0] += face[0]
            initial_point[1] += face[1]
            initial_point = tuple(initial_point)

            cv2.circle(img, initial_point, 1, (0, 0, 255), -1)

        cv2.imshow("img", img)
    
    def get_state_as_vector(self):
        #temp_list = [self.current_state["face"], 
        #             self.current_state["right_eye"], 
        #             self.current_state["left_eye"], 
        #             self.current_state["right_pupil"], 
        #             self.current_state["left_pupil"]]
        
        temp_list = [self.current_state["right_eye"],
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
