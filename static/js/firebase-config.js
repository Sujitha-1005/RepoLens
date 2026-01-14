import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";

const firebaseConfig = {
    apiKey: "AIzaSyBOFKV7u4DPLa3fpJMMEokmGd29y9XlksE",
    authDomain: "repolens-8445a.firebaseapp.com",
    projectId: "repolens-8445a",
    storageBucket: "repolens-8445a.firebasestorage.app",
    messagingSenderId: "955211302806",
    appId: "1:955211302806:web:6d35117802f37ceb903fb7",
    measurementId: "G-0Q2QNDE2LP"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const analytics = getAnalytics(app);
