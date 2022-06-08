import os
import cv2
import json
from flask import Flask, request
from google.cloud import aiplatform

app = Flask(__name__)

@app.route("/predict", methods=['POST'])
def predict():
    # Request form data (File)
    file = request.files['file']
    if file:
        # Convert to List
        image = '/tmp/' + file.filename # This is temporary directory in App Engine
        file.save(image)
        read_image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        convert = cv2.resize(read_image, (150, 150)) # Resize to 150 x 150
        convert = cv2.cvtColor(convert, cv2.COLOR_BGR2RGB) # Because default cv2 convert is BGR, so i convert to RGB first.
        request_body = [convert.tolist()] # Convert image to list
        os.remove(image) # Don't forget to delete file
        
        # Do a Predict to AI
        endpoint = aiplatform.Endpoint("projects/capstone-project-351416/locations/asia-southeast1/endpoints/3675394692771479552")
        prediction = endpoint.predict(request_body)
        max_value = max(prediction[0][0]) # Get the max value
        max_index = prediction[0][0].index(max_value) # Get the index.maxvalue

        # Identifier 
        if max_index == 0:
            makanan = "bika_ambon"
        if max_index == 1:
            makanan = "kerak_telor"
        if max_index == 2:
            makanan = "pempek"
        response_body = json.dumps(
            {
                "status": True,
                "makanan": makanan
            }
            )
        return response_body
    return json.dumps(
        {
            "status": False,
            "error": "Please add the image"
        })

# APP Run
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
