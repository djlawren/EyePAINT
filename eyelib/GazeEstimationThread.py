"""
Gaze Estimation Thread
EyePAINT

By Dean Lawrence
"""

import threading
import queue
import cv2
import time

from . import GazeEstimation
from . import FeatureExtraction

class GazeEstimationThread():
    def __init__(self, x_estimator, y_estimator, face_cascade_path, eye_cascade_path, shape_predictor_path, width, height):
        
        self._width = width
        self._height = height

        self._gaze_estimator = GazeEstimation(x_estimator, y_estimator, self._width, self._height)
        self._feature_extractor = FeatureExtraction(face_cascade_path, eye_cascade_path, shape_predictor_path)

        self._time_samples = []
        self._gaze_queue = queue.Queue(0)

        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = True
        self._thread.start()

    def run(self):
        while True:
            start_time = time.time()
            self._feature_extractor.update_feature_state(pupil_alpha=0.7)
            #self._feature_extractor.display_feature_state()

            #cv2.waitKey(1)

            #print(time.time())

            if self._gaze_estimator.is_trained():
                self._gaze_queue.put(self._gaze_estimator.predict(self._feature_extractor.get_state_as_vector()))

                end_time = time.time()
                self._time_samples.append(end_time - start_time)

    
    def get(self):
        if self._gaze_queue.qsize() == 0:
            return None
        else:
            return self._gaze_queue.get()
    
    def add_sample(self, label):
        self._gaze_estimator.add_sample(self._feature_extractor.get_state_as_vector(), label)

    def train(self):
        self._gaze_estimator.train()
    
    def test_data(self):
        self._gaze_estimator.test_data()
    
    def get_time_samples(self):
        return self._time_samples

    def get_calibration_samples(self):
        return self._gaze_estimator.x_test_errors, self._gaze_estimator.y_test_errors
    
    def get_sample_count(self):
        return len(self._gaze_estimator.data["x_labels"])
    
    def is_trained(self):
        return self._gaze_estimator.is_trained()

