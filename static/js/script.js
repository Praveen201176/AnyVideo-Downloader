/**
 * AnyVideo Downloader - Frontend JavaScript
 * Developer: dr1p7.steez
 * 
 * Security Features:
 * - Input validation
 * - XSS prevention
 * - Safe DOM manipulation
 * - Sanitized output
 */

// Global variables
let currentDownloadId = null;
let progressCheckInterval = null;

// DOM Elements
const videoUrlInput = document.getElementById('videoUrl');
const getInfoBtn = document.getElementById('getInfoBtn');
const downloadBtn = document.getElementById('downloadBtn');
const videoInfo = document.getElementById('videoInfo');
const progressSection = document.getElementById('progressSection');
const historyList = document.getElementById('historyList');

// Format bytes to human readable
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Format seconds to time
function formatTime(seconds) {
    if (!seconds || seconds === 0) return '0:00';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    if (h > 0) {
        return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Sanitize text to prevent XSS
function sanitizeText(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show error message (XSS-safe)
function showError(message, suggestion = null, details = null) {
    // Sanitize all inputs
    message = sanitizeText(message);
    suggestion = suggestion ? sanitizeText(suggestion) : null;
    details = details ? sanitizeText(details) : null;
    
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    let errorHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <div style="flex: 1;">
            <strong>${message}</strong>
    `;
    
    if (suggestion) {
        errorHTML += `<br><small><i class="fas fa-lightbulb"></i> ${suggestion}</small>`;
    }
    
    if (details && details !== message) {
        errorHTML += `<br><small style="opacity: 0.7;">${details}</small>`;
    }
    
    errorHTML += `</div>`;
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = errorHTML;
    
    document.querySelector('.main-section').insertAdjacentElement('afterbegin', errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 8000);  // Longer timeout for detailed messages
}

// Show success message (XSS-safe)
function showSuccess(message) {
    // Sanitize message
    message = sanitizeText(message);
    
    const existingSuccess = document.querySelector('.success-message');
    if (existingSuccess) {
        existingSuccess.remove();
    }
    
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    document.querySelector('.main-section').insertAdjacentElement('afterbegin', successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

// Validate URL (basic client-side check)
function isValidUrl(url) {
    if (!url) return false;
    
    // Check for common XSS patterns
    const dangerous = /(<script|javascript:|on\w+\s*=|<iframe|<embed)/i;
    if (dangerous.test(url)) {
        return false;
    }
    
    // Check for valid URL pattern
    try {
        const urlObj = new URL(url);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
        return false;
    }
}

// Get video information
async function getVideoInfo() {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        showError('Please enter a video URL');
        return;
    }
    
    // Validate URL
    if (!isValidUrl(url)) {
        showError('Invalid URL format', 'Please enter a valid HTTP or HTTPS URL');
        return;
    }
    
    getInfoBtn.disabled = true;
    getInfoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error, data.suggestion, data.details);
            return;
        }
        
        // Display video information
        document.getElementById('thumbnail').src = data.thumbnail || 'https://via.placeholder.com/320x180?text=No+Thumbnail';
        document.getElementById('videoTitle').textContent = data.title || 'Unknown Title';
        document.getElementById('uploader').textContent = data.uploader || 'Unknown';
        document.getElementById('duration').textContent = formatTime(data.duration);
        document.getElementById('views').textContent = data.view_count ? formatNumber(data.view_count) : 'N/A';
        document.getElementById('description').textContent = data.description || 'No description available';
        
        // Show video info section
        videoInfo.classList.remove('hidden');
        videoInfo.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError('Failed to get video information. Please check the URL and try again.');
        console.error('Error:', error);
    } finally {
        getInfoBtn.disabled = false;
        getInfoBtn.innerHTML = '<i class="fas fa-info-circle"></i> Get Info';
    }
}

// Start download
async function startDownload() {
    const url = videoUrlInput.value.trim();
    const quality = document.getElementById('qualitySelect').value;
    const format = document.getElementById('formatSelect').value;
    
    if (!url) {
        showError('Please enter a video URL');
        return;
    }
    
    // Validate URL
    if (!isValidUrl(url)) {
        showError('Invalid URL format', 'Please enter a valid HTTP or HTTPS URL');
        return;
    }
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, quality, format }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error, data.suggestion, data.details);
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Now';
            return;
        }
        
        // Store download ID and start monitoring progress
        currentDownloadId = data.download_id;
        
        // Show progress section
        progressSection.classList.remove('hidden');
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Start checking progress
        checkProgress();
        progressCheckInterval = setInterval(checkProgress, 1000);
        
    } catch (error) {
        showError('Failed to start download. Please try again.');
        console.error('Error:', error);
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Now';
    }
}

// Check download progress
async function checkProgress() {
    if (!currentDownloadId) return;
    
    try {
        const response = await fetch(`/api/progress/${currentDownloadId}`);
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            stopProgressCheck();
            return;
        }
        
        // Update progress bar
        const progress = data.progress || 0;
        document.getElementById('progressFill').style.width = progress + '%';
        
        // Update progress text
        let statusText = '';
        if (data.status === 'queued') {
            statusText = 'Queued...';
        } else if (data.status === 'starting') {
            statusText = 'Starting download...';
        } else if (data.status === 'downloading') {
            statusText = `Downloading: ${data.title || 'video'}`;
        } else if (data.status === 'processing') {
            statusText = 'Processing video...';
        } else if (data.status === 'completed') {
            statusText = 'Download completed!';
        } else if (data.status === 'error') {
            statusText = 'Error: ' + (data.error || 'Unknown error');
        }
        
        document.getElementById('progressText').textContent = statusText;
        
        // Update stats
        if (data.status === 'downloading' && data.speed) {
            const downloaded = formatBytes(data.downloaded || 0);
            const total = formatBytes(data.total || 0);
            const speed = formatBytes(data.speed || 0);
            const eta = data.eta ? formatTime(data.eta) : 'Unknown';
            
            document.getElementById('progressStats').textContent = 
                `${downloaded} / ${total} • ${speed}/s • ETA: ${eta}`;
        } else if (data.status === 'completed') {
            document.getElementById('progressStats').textContent = 'Video saved to downloads folder';
        } else {
            document.getElementById('progressStats').textContent = '';
        }
        
        // Handle completion
        if (data.status === 'completed') {
            stopProgressCheck();
            showSuccess('Download completed successfully!');
            loadHistory();
            
            // Reset UI
            setTimeout(() => {
                progressSection.classList.add('hidden');
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Now';
            }, 3000);
        }
        
        // Handle error
        if (data.status === 'error') {
            stopProgressCheck();
            showError(data.error || 'Download failed');
            
            setTimeout(() => {
                progressSection.classList.add('hidden');
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Now';
            }, 3000);
        }
        
    } catch (error) {
        console.error('Error checking progress:', error);
    }
}

// Stop progress checking
function stopProgressCheck() {
    if (progressCheckInterval) {
        clearInterval(progressCheckInterval);
        progressCheckInterval = null;
    }
    currentDownloadId = null;
}

// Load download history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        
        if (history.length === 0) {
            historyList.innerHTML = '<p class="empty-message">No downloads yet. Start by pasting a video URL above!</p>';
            return;
        }
        
        historyList.innerHTML = history.reverse().map(item => `
            <div class="history-item">
                <h4>${item.title || 'Unknown Title'}</h4>
                <p><i class="fas fa-link"></i> ${item.url}</p>
                <p><i class="fas fa-sliders-h"></i> Quality: ${item.quality} | Format: ${item.format}</p>
                <p><i class="fas fa-clock"></i> ${new Date(item.completed_at).toLocaleString()}</p>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Load supported sites
async function loadSupportedSites() {
    try {
        const response = await fetch('/api/supported-sites');
        const sites = await response.json();
        
        const sitesList = document.getElementById('sitesList');
        sitesList.innerHTML = sites.map(site => 
            `<span class="site-tag">${site}</span>`
        ).join('');
        
    } catch (error) {
        console.error('Error loading supported sites:', error);
    }
}

// Event listeners
getInfoBtn.addEventListener('click', getVideoInfo);
downloadBtn.addEventListener('click', startDownload);

// Allow pressing Enter to get info
videoUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        getVideoInfo();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    loadSupportedSites();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopProgressCheck();
});

