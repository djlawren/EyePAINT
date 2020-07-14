"""
Gaze Estimation
EyePAINT

By Dean Lawrence
"""

from sklearn import linear_model
import numpy as np 

class GazeEstimation():
    def __init__(self, estimator):
        
        self.data = {
            "X": [],
            "Y": []
        }

        self.estimator = estimator

    def clear_data(self):
        self.data = {
            "X": [],
            "Y": []
        }

    def add_sample(self, predictor, label):
        self.data["X"].append(predictor)
        self.data["Y"].append(label)

    def train(self):
        X = np.array(self.data["X"])
        y = np.array(self.data["Y"])

        self.estimator.fit(X, y)

    def predict(self, ):
        return self.estimator.predict(predictor)
