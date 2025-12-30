// Firebase Configuration
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyCo2sY-LTnbe48lM089nxNSmvA9AHA3FIM",
  authDomain: "collegehack.firebaseapp.com",
  projectId: "collegehack",
  storageBucket: "collegehack.firebasestorage.app",
  messagingSenderId: "502238961650",
  appId: "1:502238961650:web:0005ef459f59440b9e556b",
  measurementId: "G-TVDRCZEL4M"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export default app;
