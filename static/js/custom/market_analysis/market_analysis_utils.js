function formatNumber(value) {
    // Handle different input types
    if (typeof value === 'string') {
        // Remove any non-numeric characters except dots
        value = value.replace(/[^0-9.]/g, '');
    }
    return parseFloat(value) || 0;
}

function formatCurrency(value) {
    const num = formatNumber(value);
    if (num >= 1e9) {
        return `$${(num / 1e9).toFixed(1)}B`;
    } else if (num >= 1e6) {
        return `$${(num / 1e6).toFixed(1)}M`;
    } else if (num >= 1e3) {
        return `$${(num / 1e3).toFixed(1)}K`;
    }
    return `$${num.toFixed(0)}`;
}

function parseAnalysisData(rawData) {
    try {
        // If the data is a string, try to parse it
        if (typeof rawData === 'string') {
            try {
                return JSON.parse(rawData);
            } catch (e) {
                console.error('Error parsing string data:', e);
                throw new Error('Invalid JSON string');
            }
        }
        
        // If it's already an object, return it
        if (typeof rawData === 'object' && rawData !== null) {
            return rawData;
        }

        throw new Error('Invalid data format');
    } catch (error) {
        console.error('Error parsing analysis data:', error);
        throw error;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateDebug(message, data) {
    const debugInfo = document.getElementById('debugInfo');
    const debugContent = document.getElementById('debugContent');
    if (debugInfo && debugContent) {
        debugInfo.classList.remove('d-none');
        const timestamp = new Date().toISOString();
        const debugMessage = `
            <div class="debug-entry">
                <strong>[${timestamp}]</strong>
                <div>${message}</div>
                ${data ? `<pre class="mt-2">${JSON.stringify(data, null, 2)}</pre>` : ''}
            </div>
        `;
        debugContent.innerHTML += debugMessage;
    }
}
