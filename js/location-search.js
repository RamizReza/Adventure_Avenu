/**
 * AdventureAvenu Pre-Saved Location Search Component
 * Connects the frontend search inputs to the SQL database via /api/locations
 * Provides live autocomplete dropdown and an integrated Search Results section.
 */

(function () {
    let debounceTimer = null;
    let activeDropdown = null;

    const API_BASE = (window.location.protocol === 'file:' || (window.location.port !== '8000' && window.location.port !== ''))
        ? 'http://localhost:8000'
        : '';

    // Inject CSS for the pre-saved location autocomplete and results cards
    function injectStyles() {
        if (document.getElementById('adventure-search-styles')) return;
        const style = document.createElement('style');
        style.id = 'adventure-search-styles';
        style.textContent = `
            .location-autocomplete-container {
                position: relative;
                display: inline-block;
            }
            .location-dropdown-menu {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                min-width: 320px;
                max-height: 380px;
                overflow-y: auto;
                background: #ffffff;
                border: 1px solid #005a70;
                border-radius: 6px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.25);
                z-index: 999999;
                margin-top: 4px;
                padding: 0;
                list-style: none !important;
                text-align: left;
            }
            .location-dropdown-item {
                display: flex;
                align-items: center;
                padding: 10px 14px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.2s ease;
                color: #333333;
                text-decoration: none;
            }
            .location-dropdown-item:last-child {
                border-bottom: none;
            }
            .location-dropdown-item:hover, .location-dropdown-item.active {
                background-color: #e0f2f1;
            }
            .loc-thumb {
                width: 44px;
                height: 44px;
                border-radius: 6px;
                object-fit: cover;
                margin-right: 12px;
                flex-shrink: 0;
                background-color: #ddd;
            }
            .loc-info {
                flex-grow: 1;
                min-width: 0;
            }
            .loc-name {
                font-size: 14px;
                font-weight: bold;
                color: #005a70;
                margin: 0 0 2px 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .loc-meta {
                font-size: 12px;
                color: #666;
                margin: 0;
            }
            .loc-badge {
                display: inline-block;
                background: #e8f5e9;
                color: #2e7d32;
                font-size: 11px;
                padding: 2px 6px;
                border-radius: 10px;
                margin-left: 6px;
            }

            /* Search Results Modal / Section */
            #location-results-section {
                max-width: 1140px;
                margin: 25px auto;
                padding: 25px;
                background: #ffffff;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                position: relative;
                animation: fadeIn 0.3s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #00838f;
                padding-bottom: 12px;
                margin-bottom: 20px;
            }
            .results-header h3 {
                color: #006064;
                margin: 0;
                font-size: 22px;
            }
            .close-results-btn {
                background: #e0e0e0;
                border: none;
                color: #333;
                padding: 6px 14px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
            }
            .close-results-btn:hover {
                background: #d32f2f;
                color: #fff;
            }
            .location-cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 20px;
            }
            .location-card {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                background: #fff;
                display: flex;
                flex-direction: column;
            }
            .location-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }
            .location-card img {
                width: 100%;
                height: 180px;
                object-fit: cover;
            }
            .location-card-body {
                padding: 15px;
                display: flex;
                flex-direction: column;
                flex-grow: 1;
            }
            .location-card-body h4 {
                color: #006064;
                margin: 0 0 6px 0;
                font-size: 17px;
            }
            .location-card-city {
                font-size: 13px;
                color: #e65100;
                font-weight: bold;
                margin-bottom: 8px;
            }
            .location-card-desc {
                font-size: 13px;
                color: #555;
                line-height: 1.45;
                margin-bottom: 12px;
                flex-grow: 1;
            }
            .location-card-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top: 1px solid #eee;
                padding-top: 10px;
                margin-top: 5px;
            }
            .select-loc-btn {
                background-color: darkcyan;
                color: #fff;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                text-decoration: none;
            }
            .select-loc-btn:hover {
                background-color: #004d40;
                color: #fff;
            }
        `;
        document.head.appendChild(style);
    }

    // Fetches locations matching query from SQL backend
    async function fetchLocations(query = '') {
        try {
            const res = await fetch(`${API_BASE}/api/locations?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            return data.locations || [];
        } catch (e) {
            console.error('[LocationSearch] Error fetching locations:', e);
            return [];
        }
    }

    // Creates and attaches autocomplete dropdown to an input
    function attachAutocomplete(input) {
        if (!input || input.dataset.hasAutocomplete) return;
        input.dataset.hasAutocomplete = 'true';

        // Create dropdown container
        const dropdown = document.createElement('ul');
        dropdown.className = 'location-dropdown-menu';
        dropdown.style.display = 'none';

        // Wrap or position relative to input
        const parent = input.parentElement;
        if (getComputedStyle(parent).position === 'static') {
            parent.style.position = 'relative';
        }
        parent.appendChild(dropdown);

        input.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const val = this.value.trim();
            debounceTimer = setTimeout(async () => {
                const locations = await fetchLocations(val);
                renderDropdown(dropdown, locations, input);
            }, 250);
        });

        input.addEventListener('focus', async function () {
            const locations = await fetchLocations(this.value.trim());
            renderDropdown(dropdown, locations, input);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target) && e.target !== input) {
                dropdown.style.display = 'none';
            }
        });
    }

    function renderDropdown(dropdown, locations, input) {
        dropdown.innerHTML = '';
        if (!locations || locations.length === 0) {
            dropdown.style.display = 'none';
            return;
        }

        locations.forEach(loc => {
            const li = document.createElement('li');
            li.className = 'location-dropdown-item';
            const imgPath = loc.image_url || 'Image/maldiv.jpg';
            li.innerHTML = `
                <img src="${imgPath}" alt="${escapeHtml(loc.name)}" class="loc-thumb" onerror="this.src='Image/maldiv.jpg'">
                <div class="loc-info">
                    <div class="loc-name">${escapeHtml(loc.name)}</div>
                    <div class="loc-meta">
                        <span>📍 ${escapeHtml(loc.city)}, ${escapeHtml(loc.country)}</span>
                        <span class="loc-badge">${escapeHtml(loc.category)}</span>
                    </div>
                </div>
            `;
            li.addEventListener('click', () => {
                input.value = `${loc.city}, ${loc.country}`;
                dropdown.style.display = 'none';
                displaySearchResults(loc.city, [loc]);
            });
            dropdown.appendChild(li);
        });

        dropdown.style.display = 'block';
    }

    // Displays full search results in an integrated card grid
    async function displaySearchResults(query, preloadedList = null) {
        let resultsSection = document.getElementById('location-results-section');
        if (!resultsSection) {
            resultsSection = document.createElement('section');
            resultsSection.id = 'location-results-section';

            // Insert after hero/header section
            const header = document.querySelector('header');
            if (header && header.nextSibling) {
                header.parentNode.insertBefore(resultsSection, header.nextSibling);
            } else {
                document.body.insertBefore(resultsSection, document.body.firstChild);
            }
        }

        let locations = preloadedList;
        if (!locations) {
            locations = await fetchLocations(query);
        }

        const isFallback = locations.length === 0;
        let displayList = locations;
        if (isFallback) {
            // Show all predefined locations as suggestions
            displayList = await fetchLocations('');
        }

        resultsSection.innerHTML = `
            <div class="results-header">
                <div>
                    <h3>${isFallback ? 'No Direct Match — Explore Pre-Saved Destinations' : 'Pre-Saved Locations from Database'}</h3>
                    <p style="margin: 4px 0 0 0; color: #555; font-size: 14px;">
                        ${isFallback ? `We couldn't find "${escapeHtml(query)}", but you can choose from our saved catalog below:` : `Found ${locations.length} saved destination(s) matching your search:`}
                    </p>
                </div>
                <button class="close-results-btn" onclick="document.getElementById('location-results-section').style.display='none'">✕ Close</button>
            </div>
            <div class="location-cards-grid">
                ${displayList.map(loc => `
                    <div class="location-card">
                        <img src="${loc.image_url || 'Image/maldiv.jpg'}" alt="${escapeHtml(loc.name)}" onerror="this.src='Image/maldiv.jpg'">
                        <div class="location-card-body">
                            <h4>${escapeHtml(loc.name)}</h4>
                            <div class="location-card-city">📍 ${escapeHtml(loc.city)}, ${escapeHtml(loc.country)}</div>
                            <div class="location-card-desc">${escapeHtml(loc.description)}</div>
                            <div class="location-card-footer">
                                <span style="font-size: 12px; color: #777;"><strong>Type:</strong> ${escapeHtml(loc.category)}</span>
                                <button class="select-loc-btn" onclick="window.selectLocationForTrip('${escapeHtml(loc.name)}', '${escapeHtml(loc.city)}, ${escapeHtml(loc.country)}')">Select Destination</button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Global helper when user clicks "Select Destination"
    window.selectLocationForTrip = function (name, cityCountry) {
        // Find destination inputs on the page and fill them
        const destInputs = document.querySelectorAll('#name, input[placeholder*="Destinations"], input[placeholder*="location"], input[name="location"], input[name="destination"]');
        destInputs.forEach(inp => {
            inp.value = cityCountry;
            inp.style.backgroundColor = '#e0f7fa';
            setTimeout(() => { inp.style.backgroundColor = ''; }, 1200);
        });

        // Hide search section
        const section = document.getElementById('location-results-section');
        if (section) section.style.display = 'none';

        // Scroll back to form
        if (destInputs.length > 0) {
            destInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            destInputs[0].focus();
        }
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

    function init() {
        injectStyles();

        // 1. Identify destination / location search inputs across all pages
        const selectors = [
            '#name',
            'input.search-input',
            '#location',
            'input[name="location"]',
            'input[name="destination"]',
            'input[name="departure"]',
            'input[name="Pick-Up"]',
            'input[placeholder*="Destinations"]',
            'input[placeholder*="Destination"]',
            'input[placeholder*="location"]',
            'input[placeholder*="Location"]',
            'input[placeholder*="Take to me"]'
        ];
        const targetInputs = Array.from(document.querySelectorAll(selectors.join(', ')));

        targetInputs.forEach(input => attachAutocomplete(input));

        // 2. Intercept form submissions that previously went to Google Search
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const action = (form.getAttribute('action') || '').toLowerCase();
            const hasGoogle = action.includes('google.com/search');
            const hasDestInput = form.querySelector('#name, input[placeholder*="Destinations"], input.search-input, #location');

            if (hasGoogle || hasDestInput) {
                form.addEventListener('submit', function (e) {
                    e.preventDefault();
                    const input = form.querySelector('#name, input[placeholder*="Destinations"], input.search-input, input[name="q"], #location');
                    const q = input ? input.value.trim() : '';
                    displaySearchResults(q);
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
