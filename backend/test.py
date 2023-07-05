import pyrebase

config = {
  "apiKey": "AIzaSyDUMgCIRYPWkbIyRiKDMqtd7pZStnBGWlo",
  "authDomain": "iot-project-f52c7.firebaseapp.com",
  "projectId": "iot-project-f52c7",
  "storageBucket": "iot-project-f52c7.appspot.com",
  "messagingSenderId": "377815157173",
  "appId": "1:377815157173:web:905b4eb36000bd9f4cb1fc",
  "serviceAccount": "key.json",
  "databaseURL": "https://iot-project-f52c7-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

# Upload file
storage.child("image/gray.jpg").put("./image/1.jpg")

# Lấy URL của file đã upload
file_url = storage.child("image/gray.jpg").get_url(None)
print("succes")

# Download file
storage.child("image/gray.jpg").download("./image/test.jpg")