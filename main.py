import os
import cv2
import json
from flask import Flask, request
from google.cloud import aiplatform
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    # Request form data (File and Firebase ID Token)
    file = request.files["file"]
    auth_token = request.form["id_token"]
    
    if auth_token == "":
        return json.dumps(
            {
                "status": False,
                "error": "ID Token value can't be null"
            }
            )
    else:
        # Verify Firebase ID token
        auth_request = requests.Request()
        id_token.verify_firebase_token(auth_token, auth_request, "capstone-project-351416")
    
        if file:
            # Convert to List
            image = "/tmp/" + file.filename # This is temporary directory in App Engine
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
            
            # Identify the food
            if max_index == 0:
                makanan = "bika_ambon"
            elif max_index == 1:
                makanan = "kerak_telor"
            elif max_index == 2:
                makanan = "pempek"
            """ Wait ML renew the model
            if max_index == 0:
                makanan = "asinan"
            elif max_index == 1:
                makanan = "bika_ambon"
            elif max_index == 2:
                makanan = "kerak_telor"
            elif max_index == 3:
                makanan = "kolak"
            elif max_index == 4:
                makanan = "pempek"
            """
            response_body = json.dumps(
                {
                    "status": True,
                    "makanan": makanan
                }
                )
            return response_body
        else:
            return json.dumps(
                {
                    "status": False,
                    "error": "Please add the image"
                }
                )

# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
