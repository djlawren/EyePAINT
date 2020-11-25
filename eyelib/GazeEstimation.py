"""
Gaze Estimation
EyePAINT

By Dean Lawrence
"""

import numpy as np 
import copy
from sklearn.metrics import mean_squared_error

class GazeState():
    def __init__(self, x, y):
        self._x = x
        self._y = y
    
    def getX(self):
        return self._x

    def getY(self):
        return self._y

class GazeEstimation():
    def __init__(self, x_estimator, y_estimator, width, height):
        
        self.data = {
            "x_predictors": [],
            "x_labels": [],
            "y_predictors": [],
            "y_labels": []
        }

        self.x_estimator = x_estimator
        self.y_estimator = y_estimator

        self.width = width
        self.height = height

        self.x_test_errors = []
        self.y_test_errors = []

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
        self.data["x_labels"].append(label[0] / self.width)

        self.data["y_predictors"].append(y_features)
        self.data["y_labels"].append(label[1] / self.height)

    def train(self):
        x_predictors = np.array(self.data["x_predictors"])
        y_predictors = np.array(self.data["y_predictors"])
        
        x_labels = np.array(self.data["x_labels"])
        y_labels = np.array(self.data["y_labels"])

        self.x_estimator.fit(x_predictors, x_labels)
        self.y_estimator.fit(y_predictors, y_labels)

        self._trained = True
    
    def test_data(self):
        
        x_predictors = np.array(self.data["x_predictors"])
        y_predictors = np.array(self.data["y_predictors"])
        
        x_labels = np.array(self.data["x_labels"])
        y_labels = np.array(self.data["y_labels"])

        self.x_estimator.fit(x_predictors, x_labels)
        self.y_estimator.fit(y_predictors, y_labels)

        x_predictions = self.x_estimator.predict(x_predictors)
        y_predictions = self.y_estimator.predict(y_predictors)

        self.x_test_errors.append(mean_squared_error(x_predictions, x_labels))
        self.y_test_errors.append(mean_squared_error(y_predictions, y_labels))

        self._trained = False

    def predict(self, predictor):

        predictor.append(0)

        x_features = np.array(predictor[0:-1:2]).reshape(1, -1)
        y_features = np.array(predictor[1:-1:2]).reshape(1, -1)

        return GazeState(min(max(int(self.x_estimator.predict(x_features) * self.width), 0), self.width),
                         min(max(int(self.y_estimator.predict(y_features) * self.height), 0), self.height))
    
    def is_trained(self):
        return self._trained
