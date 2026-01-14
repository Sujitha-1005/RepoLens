import { auth } from './firebase-config.js';
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    signInAnonymously,
    updateProfile
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const authLinks = document.getElementById('auth-links');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const anonBtn = document.getElementById('anon-btn');
const logoutBtnId = 'logout-btn';
const protectedNav = document.querySelector('.protected-nav');

// Protected Routes List
const protectedRoutes = ['/analyze', '/search', '/profile'];

// Auth State Monitor
const protectedContent = document.getElementById('protected-content');
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in
        if (protectedNav) protectedNav.style.display = 'inline';
        if (protectedContent) protectedContent.style.display = 'block';

        authLinks.innerHTML = `
            <span style="margin-right: 1rem; color: var(--text-secondary);">Hi, ${user.displayName || 'Anonymous'}</span>
            <button id="${logoutBtnId}" class="btn" style="padding: 0.5rem 1rem; font-size: 0.9rem; background: var(--border-color); color: var(--text-primary);">Logout</button>
        `;

        // Attach logout listener
        document.getElementById(logoutBtnId).addEventListener('click', () => {
            signOut(auth).then(() => {
                window.location.href = "/";
            });
        });

        // Redirect if on login/register page
        if (window.location.pathname === '/login' || window.location.pathname === '/register') {
            window.location.replace('/');
        }

    } else {
        // User is signed out
        if (protectedNav) protectedNav.style.display = 'none';
        if (protectedContent) protectedContent.style.display = 'none';

        authLinks.innerHTML = `
            <a href="/login" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.9rem; color: #fff;">Login</a>
        `;

        // Redirect if on protected page
        if (protectedRoutes.some(route => window.location.pathname.startsWith(route))) {
            window.location.replace('/login');
        }
    }
});

// Login Form Handling
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        signInWithEmailAndPassword(auth, email, password)
            .then(() => {
                // Redirect handled by onAuthStateChanged
            })
            .catch((error) => {
                alert("Login Error: " + error.message);
            });
    });
}

// Register Form Handling
if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const name = document.getElementById('name').value;

        createUserWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                return updateProfile(userCredential.user, {
                    displayName: name
                });
            })
            .then(() => {
                // Redirect handled by onAuthStateChanged
            })
            .catch((error) => {
                alert("Registration Error: " + error.message);
            });
    });
}


// Anonymous Sign In
if (anonBtn) {
    anonBtn.addEventListener('click', () => {
        signInAnonymously(auth)
            .then(() => {
                // Redirect handled by onAuthStateChanged
            })
            .catch((error) => {
                console.error("Anon Auth Error", error);
                alert("Anonymous Auth Error: " + error.message);
            });
    });
}
