import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyDUMgCIRYPWkbIyRiKDMqtd7pZStnBGWlo",
  authDomain: "iot-project-f52c7.firebaseapp.com",
  databaseURL: "https://iot-project-f52c7-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "iot-project-f52c7",
  storageBucket: "iot-project-f52c7.appspot.com",
  messagingSenderId: "377815157173",
  appId: "1:377815157173:web:905b4eb36000bd9f4cb1fc"
};

const app = initializeApp(firebaseConfig);
export const storage = getStorage(app);