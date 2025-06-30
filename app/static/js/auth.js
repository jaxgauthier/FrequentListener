document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.className = 'error-message';
    }

    function showSuccess(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.className = 'success-message';
    }

    function hideMessage() {
        errorMessage.style.display = 'none';
    }

    // Login form handling
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            hideMessage();

            const formData = new FormData(loginForm);
            const data = {
                identifier: formData.get('identifier'),
                password: formData.get('password')
            };

            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Login failed');
                }
            })
            .then(data => {
                if (data && data.success) {
                    showSuccess(data.message);
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else if (data) {
                    showError(data.error || 'Login failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Network error occurred');
            });
        });
    }

    // Signup form handling
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            hideMessage();

            const formData = new FormData(signupForm);
            const data = {
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password'),
                confirm_password: formData.get('confirm_password')
            };

            // Client-side validation
            if (data.password !== data.confirm_password) {
                showError('Passwords do not match');
                return;
            }

            if (data.password.length < 6) {
                showError('Password must be at least 6 characters');
                return;
            }

            if (!/^[a-zA-Z0-9_]+$/.test(data.username)) {
                showError('Username can only contain letters, numbers, and underscores');
                return;
            }

            fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccess(data.message);
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    showError(data.error || 'Signup failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Network error occurred');
            });
        });
    }
}); 