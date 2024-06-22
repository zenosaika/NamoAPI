import tensorflow as tf
import numpy as np
import cv2

model = tf.keras.models.load_model('/app/EfficientNetB0_.h5')

def load_and_preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (125, 125))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def predict(img_path):
    # Load and preprocess the image
    input_image = load_and_preprocess_image(img_path)

    # Perform prediction using the loaded model
    predictions = model.predict(input_image)

    # Assuming your model predicts class probabilities (softmax output), get the predicted class
    predicted_class = np.argmax(predictions[0])  # Assuming batch size is 1

    return predicted_class