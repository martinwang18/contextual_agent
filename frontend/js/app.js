/**
 * Contextual Agent - Frontend JavaScript
 * Handles user interactions and API communication
 */

// Configuration
const API_BASE = window.location.origin + '/api';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const dateInput = document.getElementById('date');
const zipcodeInput = document.getElementById('zipcode');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const resultsSection = document.getElementById('results');
const resultsList = document.getElementById('resultsList');
const resultsLocation = document.querySelector('.results-location');
const resultsMetadata = document.getElementById('resultsMetadata');
const exampleButtons = document.querySelectorAll('.example-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.max = today;

    // Add event listeners
    searchForm.addEventListener('submit', handleSearch);

    // Example buttons
    exampleButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const zipcode = e.target.dataset.zipcode;
            zipcodeInput.value = zipcode;
            dateInput.value = today;
            handleSearch(e);
        });
    });

    // Auto-focus on zipcode
    zipcodeInput.focus();
});

/**
 * Handle search form submission
 */
async function handleSearch(e) {
    e.preventDefault();

    const date = dateInput.value;
    const zipcode = zipcodeInput.value;

    // Validate inputs
    if (!date || !zipcode) {
        showError('Please enter both date and zipcode');
        return;
    }

    if (!validateZipcode(zipcode)) {
        showError('Please enter a valid 5-digit USA zipcode');
        return;
    }

    // Show loading state
    hideError();
    hideResults();
    showLoading();

    try {
        // Call API
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ date, zipcode })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Search failed');
        }

        const data = await response.json();

        // Hide loading and show results
        hideLoading();

        if (data.status === 'success' && data.results && data.results.length > 0) {
            displayResults(data);
        } else {
            showError('No results found for this location and date');
        }

    } catch (error) {
        hideLoading();
        showError(`Unable to fetch results: ${error.message}`);
        console.error('Search error:', error);
    }
}

/**
 * Display search results
 */
function displayResults(data) {
    // Clear previous results
    resultsList.innerHTML = '';

    // Update location
    resultsLocation.textContent = `📍 ${data.query.location} on ${formatDate(data.query.date)}`;

    // Check if we have categorized data
    if (data.metadata && data.metadata.categorized) {
        displayCategorizedResults(data.metadata.categorized);
    } else {
        // Fallback to legacy top 5 view
        displayLegacyResults(data.results);
    }

    // Update metadata
    if (data.metadata) {
        const metaText = [];
        if (data.metadata.total_items_analyzed) {
            metaText.push(`Analyzed ${data.metadata.total_items_analyzed} items`);
        }
        if (data.metadata.response_time_ms) {
            metaText.push(`Response time: ${data.metadata.response_time_ms}ms`);
        }
        resultsMetadata.textContent = metaText.join(' • ');
    }

    // Show results section
    showResults();

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Display categorized results in tables
 */
function displayCategorizedResults(categorized) {
    // Display holidays/events (if any)
    if (categorized.holidays && categorized.holidays.length > 0) {
        displayHolidays(categorized.holidays);
        document.getElementById('holidaysSection').classList.remove('hidden');
    } else {
        document.getElementById('holidaysSection').classList.add('hidden');
    }

    // Display weather
    displayWeather(categorized.weather);

    // Display local news table
    displayNewsTable('localNewsBody', categorized.local_news);

    // Display national news table
    displayNewsTable('nationalNewsBody', categorized.national_news);

    // Show category sections
    document.getElementById('weatherSection').classList.remove('hidden');
    document.getElementById('localNewsSection').classList.remove('hidden');
    document.getElementById('nationalNewsSection').classList.remove('hidden');
    document.getElementById('top5Section').classList.add('hidden');
}

/**
 * Display holidays and special events
 */
function displayHolidays(holidayItems) {
    const holidaysContent = document.getElementById('holidaysContent');
    holidaysContent.innerHTML = '';

    holidayItems.forEach(item => {
        const card = document.createElement('div');
        const typeClass = item.metadata?.type || 'observance';
        const isFederal = item.metadata?.is_federal;

        card.className = 'holiday-card';
        if (isFederal) {
            card.classList.add('federal');
        } else if (item.category === 'event') {
            card.classList.add('event');
        }

        card.innerHTML = `
            <div class="holiday-title">${escapeHtml(item.title)}</div>
            <div class="holiday-description">${escapeHtml(item.description)}</div>
            <div class="holiday-badge">${formatCategory(typeClass)}</div>
        `;

        holidaysContent.appendChild(card);
    });
}

/**
 * Display legacy top 5 results
 */
function displayLegacyResults(results) {
    // Create result cards
    results.forEach((item, index) => {
        const card = createResultCard(item, index + 1);
        resultsList.appendChild(card);
    });

    // Hide category sections, show top 5
    document.getElementById('weatherSection').classList.add('hidden');
    document.getElementById('localNewsSection').classList.add('hidden');
    document.getElementById('nationalNewsSection').classList.add('hidden');
    document.getElementById('top5Section').classList.remove('hidden');
}

/**
 * Display weather information
 */
function displayWeather(weatherItems) {
    const weatherContent = document.getElementById('weatherContent');
    weatherContent.innerHTML = '';

    if (!weatherItems || weatherItems.length === 0) {
        weatherContent.innerHTML = '<div class="empty-state">No weather data available</div>';
        return;
    }

    weatherItems.forEach(item => {
        const card = document.createElement('div');
        card.className = 'weather-card';
        if (item.category === 'weather_alert') {
            card.classList.add('alert');
        }

        card.innerHTML = `
            <div class="weather-title">${escapeHtml(item.title)}</div>
            <div class="weather-description">${escapeHtml(item.description)}</div>
            <div class="weather-meta">
                <span class="meta-badge">${item.source}</span>
                <span class="meta-badge score">Score: ${Math.round(item.score)}</span>
            </div>
        `;

        weatherContent.appendChild(card);
    });
}

/**
 * Display news in a table
 */
function displayNewsTable(tbodyId, newsItems) {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';

    if (!newsItems || newsItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No news items available</td></tr>';
        return;
    }

    newsItems.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="rank-cell" data-label="#">${index + 1}</td>
            <td class="headline-cell" data-label="Headline">
                <span class="headline-link" title="${escapeHtml(item.description || item.title)}">
                    ${escapeHtml(item.title)}
                </span>
            </td>
            <td class="source-cell" data-label="Source">${escapeHtml(item.source)}</td>
            <td class="score-cell" data-label="Score">${Math.round(item.score)}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Create a result card element
 */
function createResultCard(item, rank) {
    const card = document.createElement('div');
    card.className = `result-card rank-${rank}`;

    // Rank badge
    const rankBadge = document.createElement('div');
    rankBadge.className = 'rank-badge';
    rankBadge.textContent = rank;

    // Content container
    const content = document.createElement('div');
    content.className = 'result-content';

    // Title with icon
    const title = document.createElement('h3');
    title.className = 'result-title';
    title.innerHTML = `${getCategoryIcon(item.category)} ${escapeHtml(item.title)}`;

    // Description
    const description = document.createElement('p');
    description.className = 'result-description';
    description.textContent = item.description;

    // Metadata
    const meta = document.createElement('div');
    meta.className = 'result-meta';

    // Category badge
    const categoryBadge = document.createElement('span');
    categoryBadge.className = 'meta-badge category';
    categoryBadge.textContent = formatCategory(item.category);

    // Score badge
    const scoreBadge = document.createElement('span');
    scoreBadge.className = 'meta-badge score';
    scoreBadge.textContent = `Score: ${Math.round(item.score)}`;

    // Source badge
    const sourceBadge = document.createElement('span');
    sourceBadge.className = 'meta-badge';
    sourceBadge.textContent = item.source;

    meta.appendChild(categoryBadge);
    meta.appendChild(scoreBadge);
    meta.appendChild(sourceBadge);

    // Assemble card
    content.appendChild(title);
    content.appendChild(description);
    content.appendChild(meta);

    card.appendChild(rankBadge);
    card.appendChild(content);

    return card;
}

/**
 * Get emoji icon for category
 */
function getCategoryIcon(category) {
    const icons = {
        'weather_alert': '⚠️',
        'severe_weather': '🌩️',
        'weather': '🌤️',
        'local_event': '🎉',
        'local_news': '📰',
        'regional_news': '📡',
        'global_news': '🌍'
    };
    return icons[category] || '📌';
}

/**
 * Format category name for display
 */
function formatCategory(category) {
    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Validate zipcode format
 */
function validateZipcode(zipcode) {
    return /^\d{5}$/.test(zipcode);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show loading state
 */
function showLoading() {
    loadingDiv.classList.remove('hidden');
}

/**
 * Hide loading state
 */
function hideLoading() {
    loadingDiv.classList.add('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    const errorText = errorDiv.querySelector('.error-text');
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
}

/**
 * Hide error message
 */
function hideError() {
    errorDiv.classList.add('hidden');
}

/**
 * Show results section
 */
function showResults() {
    resultsSection.classList.remove('hidden');
}

/**
 * Hide results section
 */
function hideResults() {
    resultsSection.classList.add('hidden');
}
