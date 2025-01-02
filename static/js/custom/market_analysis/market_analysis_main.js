function generateAnalysis() {
    // Destroy existing charts
    destroyCharts();

    // Show loading state
    document.getElementById('loadingState').classList.remove('d-none');
    document.getElementById('analysisContent').classList.add('d-none');
    document.getElementById('generateBtn').disabled = true;

    // Get CSRF token
    const csrftoken = getCookie('csrftoken');

    // Make AJAX request
    fetch(window.generateAnalysisUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Failed to generate analysis');
            });
        }
        return response.json();
    })
    .then(data => {
        // Hide loading state
        document.getElementById('loadingState').classList.add('d-none');
        document.getElementById('analysisContent').classList.remove('d-none');
        document.getElementById('generateBtn').disabled = false;

        try {
            // Check if we have valid analysis data
            if (!data.result || typeof data.result !== 'object') {
                throw new Error('Invalid analysis data format');
            }

            renderMarketAnalysis(data.result);
        } catch (error) {
            showError('Error Processing Analysis', 
                     'There was an error processing the market analysis data. Please try again.',
                     error.message);
        }
    })
    .catch(error => {
        // Hide loading state and show error
        document.getElementById('loadingState').classList.add('d-none');
        document.getElementById('analysisContent').classList.remove('d-none');
        document.getElementById('generateBtn').disabled = false;
        
        showError('Error Generating Analysis',
                 'There was an error generating the market analysis. Please try again.',
                 error.message);
    });
}

function showError(title, message, details) {
    document.getElementById('marketAnalysisData').innerHTML = `
        <div class="alert alert-danger">
            <h4 class="alert-heading">${title}</h4>
            <p>${message}</p>
            ${details ? `<hr><p class="mb-0">Error details: ${details}</p>` : ''}
        </div>
    `;
}

// Initialize analysis if there's initial data
document.addEventListener('DOMContentLoaded', function() {
    const initialDataElement = document.getElementById('initialAnalysisData');
    if (initialDataElement) {
        try {
            const initialData = parseAnalysisData(initialDataElement.textContent);
            if (initialData) {
                renderMarketAnalysis(initialData);
            }
        } catch (error) {
            showError('Error Loading Initial Data',
                     'There was an error loading the initial market analysis data. Please try generating a new analysis.',
                     error.message);
        }
    }
});
