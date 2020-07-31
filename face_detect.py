"""
Gaze Estimation MVP
EyePAINT

By Dean Lawrence
"""

import cv2
from sklearn import linear_model
import tkinter as tk
import tkinter.font as tkFont

from eyelib import FeatureExtraction, GazeEstimation, weighted_average

window = tk.Tk()
label = tk.Label(window, text="X", font=tkFont.Font(size=30))

feature_extractor = FeatureExtraction(face_cascade_path="./classifiers/haarcascade_frontalface_default.xml", 
                                      eye_cascade_path="./classifiers/haarcascade_eye.xml")
gaze_estimator = GazeEstimation(linear_model.Ridge(alpha=0.5), linear_model.Ridge(alpha=0.5))

cursor_x, cursor_y = 0, 0

def update_feature_state():
    global window, feature_extractor

    feature_extractor.update_feature_state(pupil_alpha=0.6)
    feature_extractor.display_feature_state()

    window.after(100, update_feature_state)

def update_gaze_prediction():
    global window, feature_extractor, gaze_estimator, label, cursor_x, cursor_y

    if gaze_estimator.is_trained():
        pred_x, pred_y = gaze_estimator.predict(feature_extractor.get_state_as_vector())

        cursor_x, cursor_y = weighted_average((cursor_x, cursor_y), (pred_x, pred_y), 0.5)

        label.place(x=cursor_x, y=cursor_y)
        
    window.after(100, update_gaze_prediction)

def update_data(event):
    global gaze_estimator, feature_extractor

    print(feature_extractor.get_state_as_vector())
    gaze_estimator.add_sample(feature_extractor.get_state_as_vector(), (event.x, event.y))
    print("[CONF] New sample: ({}, {})".format(event.x, event.y))

    gaze_estimator.train()
    print("[CONF] Regressors retrained")

def main():
    global window, feature_extractor, gaze_estimator, label

    #submit = tk.Button(text="Fit")
    #submit.bind("<Button 1>", lambda e: gaze_estimator.train())
    #submit.place(x=0, y=0)
    label.place(x=0, y=0)

    window.bind("<Button 1>", update_data)
    
    update_feature_state()
    update_gaze_prediction()

    window.title("EyePAINT Gaze Estimation MVP")
    window.mainloop()

    feature_extractor.release()

if __name__ == "__main__":
    main()
