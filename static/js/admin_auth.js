document.addEventListener('DOMContentLoaded', function() {
    const adminLoginForm = document.getElementById('adminLoginForm');
    const errorMessage = document.getElementById('errorMessage');
    
    adminLoginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        // Clear previous error
        errorMessage.style.display = 'none';
        
        // Basic validation
        if (!username || !password) {
            showError('Please enter both username and password');
            return;
        }
        
        // Show loading state
        const submitBtn = adminLoginForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Logging in...';
        submitBtn.disabled = true;
        
        // Send login request
        fetch('/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to admin panel
                window.location.href = data.redirect;
            } else {
                showError(data.error || 'Login failed');
            }
        })
        .catch(error => {
            console.error('Login error:', error);
            showError('Network error. Please try again.');
        })
        .finally(() => {
            // Reset button state
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
}); 