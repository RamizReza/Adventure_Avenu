/**
 * AdventureAvenu User Authentication & Session Helper
 * Checks user login status with the backend SQL database and updates navigation headers.
 */

(function () {
    const API_BASE = (window.location.protocol === 'file:' || (window.location.port !== '8000' && window.location.port !== ''))
        ? 'http://localhost:8000'
        : '';

    async function checkAuthStatus() {
        try {
            const token = localStorage.getItem('adv_session_token');
            const headers = {};
            if (token) {
                headers['Authorization'] = 'Bearer ' + token;
            }
            const response = await fetch(`${API_BASE}/api/me`, {
                credentials: 'include',
                headers: headers
            });
            const data = await response.json();
            
            if (data && data.logged_in && data.user) {
                updateNavbarForLoggedInUser(data.user);
            } else {
                localStorage.removeItem('adv_session_token');
                updateNavbarForGuestUser();
            }
        } catch (err) {
            console.warn('[AdventureAvenu] Auth check failed:', err);
        }
    }

    function updateNavbarForLoggedInUser(user) {
        const displayName = user.first_name || user.name || 'Traveler';

        // 1. Check index.html style nav (has div with Login / Sign Up)
        const loginLinks = document.querySelectorAll('a[href="./login.html"], a[href="login.html"], a[href="/login.html"]');
        loginLinks.forEach(link => {
            const container = link.parentElement;
            if (container) {
                container.innerHTML = `
                    <span style="color: #ffffff; margin-right: 15px; font-size: 14px;">
                        <i class="fa fa-user"></i> Welcome, <strong>${escapeHtml(displayName)}</strong>
                    </span>
                    <a href="/logout" onclick="window.handleLogout(event)" style="color: #ffdd57; text-decoration: none; font-weight: bold; padding: 4px 10px; border: 1px solid #ffdd57; border-radius: 4px;">
                        Logout
                    </a>
                `;
            }
        });

        // 2. Check home.html / standard ul navs
        const navUls = document.querySelectorAll('nav ul');
        navUls.forEach(ul => {
            // Avoid adding multiple times
            if (ul.querySelector('.user-auth-item')) return;

            const liUser = document.createElement('li');
            liUser.className = 'user-auth-item';
            liUser.innerHTML = `
                <span style="color: #fff; font-weight: bold; padding: 5px 8px;">
                    Welcome, ${escapeHtml(displayName)}
                </span>
            `;

            const liLogout = document.createElement('li');
            liLogout.className = 'user-auth-item';
            liLogout.innerHTML = `
                <a href="/logout" onclick="window.handleLogout(event)" style="color: #ffdd57; font-weight: bold; border: 1px solid #ffdd57; border-radius: 4px; padding: 4px 10px;">
                    Logout
                </a>
            `;

            ul.appendChild(liUser);
            ul.appendChild(liLogout);
        });

        // 3. Check simple nav with <a> tags directly (e.g., Hotel.html, Car.html)
        const directNavs = document.querySelectorAll('nav');
        directNavs.forEach(nav => {
            if (nav.querySelector('ul')) return; // handled above
            if (nav.querySelector('.user-auth-span')) return;

            const authSpan = document.createElement('span');
            authSpan.className = 'user-auth-span';
            authSpan.style.marginLeft = '20px';
            authSpan.innerHTML = `
                <span style="color: #ffffff; margin-right: 10px; font-weight: bold;">
                    Welcome, ${escapeHtml(displayName)}
                </span>
                <a href="/logout" onclick="window.handleLogout(event)" style="color: #ffdd57; font-weight: bold; border: 1px solid #ffdd57; border-radius: 4px; padding: 3px 8px;">
                    Logout
                </a>
            `;
            nav.appendChild(authSpan);
        });
    }

    function updateNavbarForGuestUser() {
        // If guest on home.html, add Login link to the nav if none exists
        const navUls = document.querySelectorAll('nav ul');
        navUls.forEach(ul => {
            if (ul.querySelector('.guest-login-item')) return;
            const hasLogin = ul.querySelector('a[href*="login.html"]');
            if (!hasLogin) {
                const li = document.createElement('li');
                li.className = 'guest-login-item';
                li.innerHTML = `<a href="./login.html" style="color: #ffdd57; font-weight: bold;">Login / Sign Up</a>`;
                ul.appendChild(li);
            }
        });
    }

    window.handleLogout = async function (e) {
        if (e) e.preventDefault();
        try {
            const token = localStorage.getItem('adv_session_token');
            const headers = {};
            if (token) {
                headers['Authorization'] = 'Bearer ' + token;
            }
            await fetch(`${API_BASE}/api/logout`, {
                method: 'POST',
                credentials: 'include',
                headers: headers
            });
        } catch (err) {
            console.error('Logout error:', err);
        }
        localStorage.removeItem('adv_session_token');
        window.location.href = './login.html';
    };

    function escapeHtml(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAuthStatus);
    } else {
        checkAuthStatus();
    }
})();
