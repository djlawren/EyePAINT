"""
Gaze Estimation
EyePAINT

By Dean Lawrence
"""

from eyelib import FeatureExtraction, GazeEstimation

def main():
    feature_extractor = FeatureExtraction("./classifiers/haarcascade_frontalface_default.xml", "./classifiers/haarcascade_eye.xml")
    gaze_estimator = GazeEstimation(linear_model.Ridge(alpha=0.5))

    while True:

        feature_extractor.update_feature_state(pupil_alpha=0.7)
        feature_extractor.display_feature_state()

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

if __name__ == "__main__":
    main()
