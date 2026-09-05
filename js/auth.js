/**
 * Victoria International College - Authentication Module
 * Manages Google, LinkedIn, and Email login, session tokens, and User UI state.
 */

(function() {
  'use strict';

  const AUTH_TOKEN_KEY = 'vic_auth_token';
  let currentUser = null;

  // Universal API Base URL Resolver
  window.getVicApiUrl = function(endpoint) {
    if (!endpoint) return '';
    if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) return endpoint;
    if (!endpoint.startsWith('/')) endpoint = '/' + endpoint;

    let base = window.VIC_API_BASE || '';
    if (!base) {
      try {
        const loc = window.location;
        const isLocal = loc.hostname === 'localhost' || loc.hostname === '127.0.0.1' || loc.hostname === '';
        if (loc.protocol === 'file:' || (isLocal && loc.port !== '5055')) {
          base = 'http://127.0.0.1:5055';
        }
      } catch (e) {
        base = 'http://127.0.0.1:5055';
      }
    }
    return base + endpoint;
  };

  const VicAuth = {
    getToken() {
      return localStorage.getItem(AUTH_TOKEN_KEY);
    },

    setToken(token) {
      if (token) {
        localStorage.setItem(AUTH_TOKEN_KEY, token);
      } else {
        localStorage.removeItem(AUTH_TOKEN_KEY);
      }
    },

    getUser() {
      return currentUser;
    },

    isAuthenticated() {
      return !!currentUser;
    },

    isAdmin() {
      return currentUser && currentUser.role === 'admin';
    },

    async init() {
      this.createAuthModalDOM();
      this.bindEvents();

      const token = this.getToken();
      if (token) {
        try {
          const res = await fetch(window.getVicApiUrl('/api/auth/me'), {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const data = await res.json();
          if (data.authenticated && data.user) {
            currentUser = data.user;
          } else {
            this.setToken(null);
            currentUser = null;
          }
        } catch (e) {
          console.warn('Auth check failed:', e);
        }
      }

      this.renderUserUI();
    },

    async login(email, password) {
      try {
        const apiUrl = window.getVicApiUrl('/api/auth/login');
        const res = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Login failed');
        }
        this.setToken(data.token);
        currentUser = data.user;
        this.renderUserUI();
        this.closeAuthModal();
        this.showToast(`Welcome back, ${currentUser.name}!`, 'success');
        return data;
      } catch (err) {
        if (err.message && (err.message.includes('fetch') || err.message.includes('NetworkError') || err.message.includes('Failed to fetch') || err.message.includes('Network request failed'))) {
          throw new Error('Cannot connect to backend server. Please verify "python server.py" is running at http://localhost:5055.');
        }
        throw err;
      }
    },

    async register(name, email, password) {
      try {
        const apiUrl = window.getVicApiUrl('/api/auth/register');
        const res = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || 'Registration failed');
        }
        this.setToken(data.token);
        currentUser = data.user;
        this.renderUserUI();
        this.closeAuthModal();
        this.showToast(`Welcome to Victoria College, ${currentUser.name}!`, 'success');
        return data;
      } catch (err) {
        if (err.message && (err.message.includes('fetch') || err.message.includes('NetworkError') || err.message.includes('Failed to fetch') || err.message.includes('Network request failed'))) {
          throw new Error('Cannot connect to backend server. Please verify "python server.py" is running at http://localhost:5055.');
        }
        throw err;
      }
    },

    async loginWithGoogle(mockEmail, mockName) {
      // Prompt user or handle Google One-Tap / Social Sign-in
      let email = mockEmail;
      let name = mockName;

      if (!email) {
        const input = prompt("Google Account Sign-in:\nEnter your Google Email (e.g. mack.chen@viccollege.com):", "mack.chen@viccollege.com");
        if (!input) return;
        email = input.trim();
        name = email.split('@')[0].replace('.', ' ').replace(/\b\w/g, l => l.toUpperCase());
      }

      try {
        const avatar_url = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`;
        const res = await fetch(window.getVicApiUrl('/api/auth/oauth/google'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, name, avatar_url })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Google login failed');

        this.setToken(data.token);
        currentUser = data.user;
        this.renderUserUI();
        this.closeAuthModal();
        this.showToast(`Signed in with Google as ${currentUser.name}`, 'success');
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async loginWithLinkedIn(mockEmail, mockName) {
      let email = mockEmail;
      let name = mockName;

      if (!email) {
        const input = prompt("LinkedIn Account Sign-in:\nEnter your LinkedIn Email (e.g. professional@linkedin.com):", "alex.wang@linkedin.com");
        if (!input) return;
        email = input.trim();
        name = email.split('@')[0].replace('.', ' ').replace(/\b\w/g, l => l.toUpperCase());
      }

      try {
        const avatar_url = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(email)}`;
        const res = await fetch(window.getVicApiUrl('/api/auth/oauth/linkedin'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, name, avatar_url })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'LinkedIn login failed');

        this.setToken(data.token);
        currentUser = data.user;
        this.renderUserUI();
        this.closeAuthModal();
        this.showToast(`Signed in with LinkedIn as ${currentUser.name}`, 'success');
      } catch (err) {
        this.showToast(err.message, 'error');
      }
    },

    async logout() {
      const token = this.getToken();
      if (token) {
        try {
          await fetch(window.getVicApiUrl('/api/auth/logout'), {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (e) {
          // ignore
        }
      }
      this.setToken(null);
      currentUser = null;
      this.renderUserUI();
      this.showToast('You have been logged out.', 'info');

      // If on admin page, redirect to home
      if (window.location.pathname.includes('/admin')) {
        window.location.href = '/';
      }
    },

    renderUserUI() {
      // 1. Desktop Navigation User Container
      const desktopNavSocial = document.querySelector('.nav-social-icons');
      if (desktopNavSocial) {
        let userBadge = document.getElementById('vic-user-nav-badge');
        if (!userBadge) {
          userBadge = document.createElement('div');
          userBadge.id = 'vic-user-nav-badge';
          userBadge.className = 'vic-user-nav-wrapper';
          desktopNavSocial.appendChild(userBadge);
        }

        if (currentUser) {
          userBadge.innerHTML = `
            <div class="vic-user-pill js-toggle-user-dropdown" title="${currentUser.email}">
              <img src="${currentUser.avatar_url}" alt="${currentUser.name}" class="vic-user-avatar">
              <span class="vic-user-name">${currentUser.name.split(' ')[0]}</span>
              ${currentUser.role === 'admin' ? '<span class="vic-badge-admin">Admin</span>' : ''}
              <i class="fa-solid fa-chevron-down vic-arrow-icon"></i>
            </div>
            <div class="vic-user-dropdown" id="vic-user-dropdown">
              <div class="user-dropdown-header">
                <strong>${currentUser.name}</strong>
                <small>${currentUser.email}</small>
                <span class="user-provider-tag">${currentUser.provider.toUpperCase()}</span>
              </div>
              <div class="user-dropdown-divider"></div>
              ${currentUser.role === 'admin' ? `
                <a href="/admin" class="user-dropdown-item admin-link">
                  <i class="fa-solid fa-gauge-high"></i> Admin Portal
                </a>
              ` : ''}
              <a href="#consultation" class="user-dropdown-item js-go-consult">
                <i class="fa-solid fa-calendar-check"></i> My Consultations
              </a>
              <button type="button" class="user-dropdown-item logout-item js-btn-logout">
                <i class="fa-solid fa-arrow-right-from-bracket"></i> Sign Out
              </button>
            </div>
          `;
        } else {
          userBadge.innerHTML = `
            <button type="button" class="vic-btn-signin js-open-auth-modal" aria-label="Sign In / Register">
              <i class="fa-regular fa-circle-user"></i>
              <span>Sign In</span>
            </button>
          `;
        }
      }

      // 2. Mobile Drawer User Section
      const mobileDrawer = document.querySelector('.mobile-nav-drawer');
      if (mobileDrawer) {
        let mobileAuthBox = document.getElementById('vic-mobile-auth-box');
        if (!mobileAuthBox) {
          mobileAuthBox = document.createElement('div');
          mobileAuthBox.id = 'vic-mobile-auth-box';
          mobileAuthBox.className = 'mobile-auth-section';
          const header = mobileDrawer.querySelector('.mobile-drawer-header');
          if (header) {
            header.insertAdjacentElement('afterend', mobileAuthBox);
          }
        }

        if (currentUser) {
          mobileAuthBox.innerHTML = `
            <div class="mobile-user-card">
              <img src="${currentUser.avatar_url}" alt="${currentUser.name}" class="mobile-avatar">
              <div class="mobile-user-details">
                <strong>${currentUser.name}</strong>
                <small>${currentUser.email}</small>
                <span class="role-badge ${currentUser.role}">${currentUser.role.toUpperCase()}</span>
              </div>
            </div>
            ${currentUser.role === 'admin' ? `
              <a href="/admin" class="mobile-admin-btn">
                <i class="fa-solid fa-shield-halved"></i> Access Admin Dashboard
              </a>
            ` : ''}
            <button type="button" class="mobile-logout-btn js-btn-logout">
              <i class="fa-solid fa-arrow-right-from-bracket"></i> Log Out
            </button>
          `;
        } else {
          mobileAuthBox.innerHTML = `
            <button type="button" class="mobile-signin-btn js-open-auth-modal">
              <i class="fa-solid fa-right-to-bracket"></i> Student &amp; Staff Login
            </button>
          `;
        }
      }

      // Re-attach dropdown & modal click events
      this.bindUserUIEvents();

      // Notify other modules of auth state change
      window.dispatchEvent(new CustomEvent('vic-auth-changed', { detail: { user: currentUser } }));
    },

    bindUserUIEvents() {
      // Open modal buttons
      document.querySelectorAll('.js-open-auth-modal').forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          this.openAuthModal();
        };
      });

      // Logout buttons
      document.querySelectorAll('.js-btn-logout').forEach(btn => {
        btn.onclick = (e) => {
          e.preventDefault();
          this.logout();
        };
      });

      // Dropdown toggle
      const toggle = document.querySelector('.js-toggle-user-dropdown');
      const dropdown = document.getElementById('vic-user-dropdown');
      if (toggle && dropdown) {
        toggle.onclick = (e) => {
          e.stopPropagation();
          dropdown.classList.toggle('show');
        };
        document.addEventListener('click', () => {
          dropdown.classList.remove('show');
        });
      }
    },

    createAuthModalDOM() {
      if (document.getElementById('vic-auth-modal')) return;

      const modal = document.createElement('div');
      modal.id = 'vic-auth-modal';
      modal.className = 'vic-auth-modal-backdrop';
      modal.innerHTML = `
        <div class="vic-auth-modal-box">
          <button type="button" class="vic-auth-close js-close-auth-modal" aria-label="Close">
            <i class="fa-solid fa-xmark"></i>
          </button>

          <div class="vic-auth-modal-header">
            <img src="images/vic_logo.png" alt="Victoria College" class="auth-logo">
            <h3 id="vic-auth-modal-title">Welcome to Victoria College</h3>
            <p id="vic-auth-modal-sub">Sign in to access student grants, save AI conversations, and track applications.</p>
          </div>

          <!-- Social OAuth Buttons -->
          <div class="vic-social-auth-group">
            <button type="button" class="vic-social-btn btn-google js-auth-google">
              <svg viewBox="0 0 24 24" width="20" height="20" class="social-icon">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
              </svg>
              <span>Continue with Google</span>
            </button>

            <button type="button" class="vic-social-btn btn-linkedin js-auth-linkedin">
              <svg viewBox="0 0 24 24" width="20" height="20" class="social-icon">
                <path fill="#0A66C2" d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
              </svg>
              <span>Continue with LinkedIn</span>
            </button>
          </div>

          <div class="vic-auth-divider">
            <span>or use email</span>
          </div>

          <!-- Tabs for Email Login vs Register -->
          <div class="vic-auth-tabs">
            <button type="button" class="auth-tab-btn active" data-tab="login">Sign In</button>
            <button type="button" class="auth-tab-btn" data-tab="register">Create Account</button>
          </div>

          <!-- Login Form -->
          <form id="vic-form-login" class="vic-auth-form active">
            <div class="auth-input-group">
              <label for="login-email">Email Address</label>
              <input type="email" id="login-email" placeholder="name@example.com" required autocomplete="email">
            </div>
            <div class="auth-input-group">
              <label for="login-password">Password</label>
              <input type="password" id="login-password" placeholder="••••••••" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn-auth-submit">Sign In to Victoria</button>
            <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
              <span style="color: #64748b;">Admin Demo:</span>
              <button type="button" class="btn-quick-fill-admin js-quick-admin" style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 3px 8px; font-size: 11px; cursor: pointer; color: #1e293b; font-weight: 500;">
                <i class="fa-solid fa-user-shield" style="color: #b91c1c; margin-right: 4px;"></i> Quick-Fill Admin
              </button>
            </div>
          </form>

          <!-- Register Form -->
          <form id="vic-form-register" class="vic-auth-form">
            <div class="auth-input-group">
              <label for="reg-name">Full Name</label>
              <input type="text" id="reg-name" placeholder="Alex Zhang" required autocomplete="name">
            </div>
            <div class="auth-input-group">
              <label for="reg-email">Email Address</label>
              <input type="email" id="reg-email" placeholder="name@example.com" required autocomplete="email">
            </div>
            <div class="auth-input-group">
              <label for="reg-password">Create Password (min 6 chars)</label>
              <input type="password" id="reg-password" placeholder="••••••••" minlength="6" required autocomplete="new-password">
            </div>
            <button type="submit" class="btn-auth-submit">Create My Account</button>
          </form>

          <div class="vic-auth-footer-note">
            <span>Registered under Ontario Career Colleges Act, 2005</span>
          </div>
        </div>
      `;

      document.body.appendChild(modal);
    },

    bindEvents() {
      // Close button
      document.querySelectorAll('.js-close-auth-modal').forEach(btn => {
        btn.onclick = () => this.closeAuthModal();
      });

      const modal = document.getElementById('vic-auth-modal');
      if (modal) {
        modal.onclick = (e) => {
          if (e.target === modal) this.closeAuthModal();
        };
      }

      // Tab switcher
      document.querySelectorAll('.auth-tab-btn').forEach(btn => {
        btn.onclick = () => {
          document.querySelectorAll('.auth-tab-btn').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.vic-auth-form').forEach(f => f.classList.remove('active'));
          btn.classList.add('active');
          const tab = btn.dataset.tab;
          const form = document.getElementById(`vic-form-${tab}`);
          if (form) form.classList.add('active');
        };
      });

      // Google & LinkedIn triggers
      document.querySelectorAll('.js-auth-google').forEach(btn => {
        btn.onclick = () => this.loginWithGoogle();
      });

      document.querySelectorAll('.js-auth-linkedin').forEach(btn => {
        btn.onclick = () => this.loginWithLinkedIn();
      });

      // Quick fill admin credentials
      document.querySelectorAll('.js-quick-admin').forEach(btn => {
        btn.onclick = () => {
          const emailInput = document.getElementById('login-email');
          const passInput = document.getElementById('login-password');
          if (emailInput) emailInput.value = 'admin@viccollege.com';
          if (passInput) passInput.value = 'admin123';
        };
      });

      // Login form submit
      const loginForm = document.getElementById('vic-form-login');
      if (loginForm) {
        loginForm.onsubmit = async (e) => {
          e.preventDefault();
          const email = document.getElementById('login-email').value;
          const password = document.getElementById('login-password').value;
          try {
            await this.login(email, password);
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        };
      }

      // Register form submit
      const regForm = document.getElementById('vic-form-register');
      if (regForm) {
        regForm.onsubmit = async (e) => {
          e.preventDefault();
          const name = document.getElementById('reg-name').value;
          const email = document.getElementById('reg-email').value;
          const password = document.getElementById('reg-password').value;
          try {
            await this.register(name, email, password);
          } catch (err) {
            this.showToast(err.message, 'error');
          }
        };
      }
    },

    openAuthModal(tab = 'login') {
      const modal = document.getElementById('vic-auth-modal');
      if (!modal) return;
      modal.classList.add('active');

      const targetTabBtn = modal.querySelector(`.auth-tab-btn[data-tab="${tab}"]`);
      if (targetTabBtn) targetTabBtn.click();
    },

    closeAuthModal() {
      const modal = document.getElementById('vic-auth-modal');
      if (modal) modal.classList.remove('active');
    },

    showToast(message, type = 'info') {
      let toast = document.getElementById('vic-auth-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'vic-auth-toast';
        toast.className = 'vic-auth-toast';
        document.body.appendChild(toast);
      }
      toast.className = `vic-auth-toast active ${type}`;
      toast.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-info'}"></i>
        <span>${message}</span>
      `;
      setTimeout(() => {
        toast.classList.remove('active');
      }, 3500);
    }
  };

  window.VicAuth = VicAuth;
  document.addEventListener('DOMContentLoaded', () => {
    VicAuth.init();
  });
})();
