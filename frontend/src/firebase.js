import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
  apiKey: "AIzaSyCz5BvTp9G3D41-qFDjohmWPbc2NKSHObI",
  authDomain: "queue-30b90.firebaseapp.com",
  projectId: "queue-30b90",
  storageBucket: "queue-30b90.firebasestorage.app",
  messagingSenderId: "753544000309",
  appId: "1:753544000309:web:3f024e00829ef08058927c",
  measurementId: "G-0NCRM7MZB4"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);