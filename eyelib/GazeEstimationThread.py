"""
Gaze Estimation Thread
EyePAINT

By Dean Lawrence
"""

import threading
import queue

from . import GazeEstimation
from . import FeatureExtraction

class GazeEstimationThread():
    def __init__(self, x_estimator, y_estimator, face_cascade_path, eye_cascade_path, shape_predictor_path, width, height):
        
        self.width = width
        self.height = height

        self.gaze_estimator = GazeEstimation(x_estimator, y_estimator)
        self.feature_extractor = FeatureExtraction(face_cascade_path, eye_cascade_path, shape_predictor_path)

        self.gaze_queue = queue.Queue(0)

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        while True:
            self.feature_extractor.update_feature_state()
            self.gaze_queue.put(self.gaze_estimator.predict(self.feature_extractor.get_state_as_vector()))
