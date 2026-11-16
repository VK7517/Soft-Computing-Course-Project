/* ==================================================
   AUTHENTICATION MODULE (auth.js)
   Register, Login, Session Management, Logout, Toasts
   ================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Register Page Form if present
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    setupRegisterForm(registerForm);
  }

  // Initialize Login Page Form if present
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    setupLoginForm(loginForm);
  }

  // Setup Password Visibility Toggles
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const input = btn.previousElementSibling || btn.parentElement.querySelector('input');
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          btn.textContent = 'Hide';
        } else {
          input.type = 'password';
          btn.textContent = 'Show';
        }
      }
    });
  });
});

function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function setupRegisterForm(form) {
  const passwordInput = document.getElementById('regPassword');
  const strengthFill = document.getElementById('strengthFill');

  if (passwordInput && strengthFill) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      strengthFill.className = 'password-strength-fill';
      if (val.length === 0) {
        strengthFill.style.width = '0%';
      } else if (val.length < 6) {
        strengthFill.classList.add('strength-weak');
      } else if (val.length < 10 || !/\d/.test(val)) {
        strengthFill.classList.add('strength-medium');
      } else {
        strengthFill.classList.add('strength-strong');
      }
    });
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('regName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;

    if (!name || !email || !password) {
      showToast('Please fill in all required fields.', 'error');
      return;
    }

    if (password !== confirmPassword) {
      showToast('Passwords do not match.', 'error');
      return;
    }

    if (password.length < 6) {
      showToast('Password must be at least 6 characters.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || 'Registration failed.', 'error');
        return;
      }

      showToast('Registration successful! Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1000);

    } catch (err) {
      console.error(err);
      showToast('Network error during registration.', 'error');
    }
  });
}

function setupLoginForm(form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
      showToast('Please enter both email and password.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();
      if (!res.ok) {
        showToast(data.error || 'Login failed.', 'error');
        return;
      }

      showToast('Login successful! Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 800);

    } catch (err) {
      console.error(err);
      showToast('Network error during login.', 'error');
    }
  });
}

async function performLogout() {
  try {
    await fetch('/api/logout', { method: 'POST' });
    showToast('Logged out.', 'info');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 500);
  } catch (err) {
    console.error(err);
    window.location.href = 'login.html';
  }
}
