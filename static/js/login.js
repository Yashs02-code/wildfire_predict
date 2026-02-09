// Import Firebase modules
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js';
import {
    getAuth,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';

// Initialize Firebase with config from server
const firebaseConfig = window.FIREBASE_CONFIG;
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Helper function to show messages
function showMessage(message, type = 'danger') {
    const messageDiv = document.getElementById('auth-message');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    messageDiv.classList.remove('d-none');

    setTimeout(() => {
        messageDiv.classList.add('d-none');
    }, 5000);
}

// Helper function to toggle loading state
function setLoading(formType, isLoading) {
    const btnText = document.getElementById(`${formType}-btn-text`);
    const spinner = document.getElementById(`${formType}-spinner`);
    const form = document.getElementById(`${formType}-form`);

    if (isLoading) {
        spinner.classList.remove('d-none');
        form.querySelector('button[type="submit"]').disabled = true;
    } else {
        spinner.classList.add('d-none');
        form.querySelector('button[type="submit"]').disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Login Form Handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            setLoading('login', true);

            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            try {
                const userCredential = await signInWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;

                // Get Firebase ID token
                const idToken = await user.getIdToken();

                // Verify token with backend and create session
                const response = await fetch('/api/auth/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ token: idToken })
                });

                if (response.ok) {
                    showMessage('✅ Login successful! Redirecting to dashboard...', 'success');

                    // Redirect to dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    throw new Error('Session verification failed');
                }

            } catch (error) {
                setLoading('login', false);
                let errorMessage = 'Login failed. ';

                switch (error.code) {
                    case 'auth/invalid-email':
                        errorMessage = '❌ Invalid email address format.';
                        break;
                    case 'auth/user-disabled':
                        errorMessage = '❌ This account has been disabled.';
                        break;
                    case 'auth/user-not-found':
                        errorMessage = '❌ No account found! Please register first by clicking the "Register" tab above.';
                        break;
                    case 'auth/wrong-password':
                        errorMessage = '❌ Incorrect password. Please try again.';
                        break;
                    case 'auth/invalid-credential':
                        errorMessage = '❌ Invalid credentials. Please check your email and password, or register if you don\'t have an account.';
                        break;
                    case 'auth/too-many-requests':
                        errorMessage = '❌ Too many failed attempts. Please try again later.';
                        break;
                    default:
                        errorMessage = '❌ ' + error.message;
                }

                showMessage(errorMessage, 'danger');
            }
        });
    }

    // Register Form Handler
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            setLoading('register', true);

            const name = document.getElementById('register-name').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;

            try {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                const user = userCredential.user;

                // Get Firebase ID token
                const idToken = await user.getIdToken();

                // Verify token with backend and create session
                const response = await fetch('/api/auth/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ token: idToken })
                });

                if (response.ok) {
                    showMessage('✅ Account created successfully! Welcome to WildFire AI. Redirecting...', 'success');

                    // Redirect to dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    throw new Error('Session verification failed');
                }

            } catch (error) {
                setLoading('register', false);
                let errorMessage = 'Registration failed. ';

                switch (error.code) {
                    case 'auth/email-already-in-use':
                        errorMessage = '❌ This email is already registered! Please use the "Login" tab to sign in.';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = '❌ Invalid email address format.';
                        break;
                    case 'auth/operation-not-allowed':
                        errorMessage = '❌ Email/password registration is not enabled. Please contact support.';
                        break;
                    case 'auth/weak-password':
                        errorMessage = '❌ Password is too weak! Please use at least 6 characters.';
                        break;
                    default:
                        errorMessage = '❌ ' + error.message;
                }

                showMessage(errorMessage, 'danger');
            }
        });
    }
});
