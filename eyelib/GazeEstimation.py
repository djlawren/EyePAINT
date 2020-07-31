"""
Gaze Estimation
EyePAINT

By Dean Lawrence
"""

import numpy as np 
import copy

class GazeEstimation():
    def __init__(self, x_estimator, y_estimator):
        
        self.data = {
            "x_predictors": [],
            "x_labels": [],
            "y_predictors": [],
            "y_labels": []
        }

        self.x_estimator = x_estimator
        self.y_estimator = y_estimator

        self._trained = False

    def clear_data(self):
        self.data = {
            "x_predictors": [],
            "x_labels": [],
            "y_predictors": [],
            "y_labels": []
        }

        self._trained = False

    def add_sample(self, predictor, label):

        predictor.append(0)

        x_features = predictor[0:-1:2]
        y_features = predictor[1:-1:2]

        self.data["x_predictors"].append(x_features)
        self.data["x_labels"].append(label[0])

        self.data["y_predictors"].append(y_features)
        self.data["y_labels"].append(label[1])

    def train(self):
        x_predictors = np.array(self.data["x_predictors"])
        y_predictors = np.array(self.data["y_predictors"])
        
        x_labels = np.array(self.data["x_labels"])
        y_labels = np.array(self.data["y_labels"])

        self.x_estimator.fit(x_predictors, x_labels)
        self.y_estimator.fit(y_predictors, y_labels)

        self._trained = True

    def predict(self, predictor):

        predictor.append(0)

        x_features = np.array(predictor[0:-1:2]).reshape(1, -1)
        y_features = np.array(predictor[1:-1:2]).reshape(1, -1)

        return (int(self.x_estimator.predict(x_features)),
                int(self.y_estimator.predict(y_features)))
    
    def is_trained(self):
        return self._trained
