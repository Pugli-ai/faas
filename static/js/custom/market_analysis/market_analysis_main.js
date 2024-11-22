function generateAnalysis() {
    console.log('Starting generateAnalysis');
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
    .then(response => response.json())
    .then(data => {
        console.log('Received response:', data);
        // Hide loading state
        document.getElementById('loadingState').classList.add('d-none');
        document.getElementById('analysisContent').classList.remove('d-none');
        document.getElementById('generateBtn').disabled = false;

        try {
            if (data.error) {
                throw new Error(data.error);
            }

            // Parse the JSON result if it's a string
            const analysisData = typeof data.result === 'string' ? JSON.parse(data.result) : data.result;
            
            if (!analysisData || typeof analysisData !== 'object') {
                throw new Error('Invalid analysis data format');
            }

            renderMarketAnalysis(analysisData);
        } catch (error) {
            console.error('Error parsing analysis data:', error);
            document.getElementById('marketAnalysisData').innerHTML = `
                <div class="alert alert-danger">
                    <h4 class="alert-heading">Error Processing Analysis Data</h4>
                    <p>There was an error processing the market analysis data. Please try again.</p>
                    <hr>
                    <p class="mb-0">Error details: ${error.message}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Network or processing error:', error);
        // Hide loading state and show error
        document.getElementById('loadingState').classList.add('d-none');
        document.getElementById('analysisContent').classList.remove('d-none');
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('marketAnalysisData').innerHTML = `
            <div class="alert alert-danger">
                <h4 class="alert-heading">Error Generating Analysis</h4>
                <p>There was an error generating the market analysis. Please try again.</p>
                <hr>
                <p class="mb-0">Error details: ${error.message}</p>
            </div>
        `;
    });
}

// Initialize analysis if there's initial data
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Add error event listener
    window.addEventListener('error', function(event) {
        updateDebug('JavaScript Error:', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    });

    const initialDataElement = document.getElementById('initialAnalysisData');
    if (initialDataElement) {
        try {
            console.log('Initial data element found:', initialDataElement.textContent);
            const initialData = parseAnalysisData(initialDataElement.textContent);
            console.log('Parsed initial data:', initialData);
            renderMarketAnalysis(initialData);
        } catch (error) {
            console.error('Error rendering initial data:', error);
            document.getElementById('marketAnalysisData').innerHTML = `
                <div class="alert alert-danger">
                    <h4 class="alert-heading">Error Loading Initial Data</h4>
                    <p>There was an error loading the initial market analysis data. Please try generating a new analysis.</p>
                    <hr>
                    <p class="mb-0">Error details: ${error.message}</p>
                </div>
            `;
        }
    } else {
        console.log('No initial data element found');
    }
});
