// Firebase configuration
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, updateDoc, collection, getDocs } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth();
const db = getFirestore();

// Elements
const authSection = document.getElementById("auth-section");
const mainSection = document.getElementById("main-section");
const loginBtn = document.getElementById("login-btn");
const signupBtn = document.getElementById("signup-btn");
const logoutBtn = document.getElementById("logout-btn");
const matchForm = document.getElementById("match-form");
const opponentSelect = document.getElementById("opponent");
const userNameSpan = document.getElementById("user-name");
const userEloSpan = document.getElementById("user-elo");

// Auth functions
async function login(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    loadUser(userCredential.user.uid);
  } catch (error) {
    alert("Login failed: " + error.message);
  }
}

async function signup(email, password) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const userId = userCredential.user.uid;
    await setDoc(doc(db, "users", userId), { elo: 1000 });
    loadUser(userId);
  } catch (error) {
    alert("Signup failed: " + error.message);
  }
}

async function logout() {
  await signOut(auth);
  authSection.style.display = "block";
  mainSection.style.display = "none";
}

// Load user data
async function loadUser(userId) {
  const userDoc = await getDoc(doc(db, "users", userId));
  if (userDoc.exists()) {
    const userData = userDoc.data();
    userNameSpan.textContent = auth.currentUser.email;
    userEloSpan.textContent = userData.elo;

    // Load opponents
    const opponentsSnap = await getDocs(collection(db, "users"));
    opponentSelect.innerHTML = "";
    opponentsSnap.forEach(doc => {
      if (doc.id !== userId) {
        const option = document.createElement("option");
        option.value = doc.id;
        option.textContent = doc.data().email || doc.id;
        opponentSelect.appendChild(option);
      }
    });

    authSection.style.display = "none";
    mainSection.style.display = "block";
  }
}

// Record match
matchForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const opponentId = opponentSelect.value;
  const points = parseInt(document.getElementById("points").value);

  const userId = auth.currentUser.uid;
  const userRef = doc(db, "users", userId);
  const opponentRef = doc(db, "users", opponentId);

  const userDoc = await getDoc(userRef);
  const opponentDoc = await getDoc(opponentRef);

  if (userDoc.exists() && opponentDoc.exists()) {
    const userElo = userDoc.data().elo;
    const opponentElo = opponentDoc.data().elo;

    // Elo calculation
    const k = 32;
    const expectedScore = 1 / (1 + 10 ** ((opponentElo - userElo) / 400));
    const newUserElo = userElo + k * (points > 0 ? 1 : 0 - expectedScore);

    const expectedScoreOpponent = 1 - expectedScore;
    const newOpponentElo = opponentElo + k * (points < 0 ? 1 : 0 - expectedScoreOpponent);

    // Update database
    await updateDoc(userRef, { elo: Math.round(newUserElo) });
    await updateDoc(opponentRef, { elo: Math.round(newOpponentElo) });

    alert("Match recorded!");
    loadUser(userId);
  }
});

// Event listeners
loginBtn.addEventListener("click", () => login(email.value, password.value));
signupBtn.addEventListener("click", () => signup(email.value, password.value));
logoutBtn.addEventListener("click", logout);
