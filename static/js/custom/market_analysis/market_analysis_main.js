function generateAnalysis() {
    console.log('Starting market analysis generation');
    
    try {
        // Show loading state
        document.getElementById('loadingState').classList.remove('d-none');
        document.getElementById('analysisContent').classList.add('d-none');
        document.getElementById('generateBtn').disabled = true;
        console.log('UI updated to loading state');

        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        console.log('CSRF token retrieved');

        // Make AJAX request
        console.log('Making API request to:', window.generateAnalysisUrl);
        fetch(window.generateAnalysisUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            console.log('Received response:', response);
            if (!response.ok) {
                return response.json().then(data => {
                    console.error('Error response:', data);
                    throw new Error(data.error || 'Failed to generate analysis');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Parsed response data:', data);
            
            // Hide loading state
            document.getElementById('loadingState').classList.add('d-none');
            document.getElementById('analysisContent').classList.remove('d-none');
            document.getElementById('generateBtn').disabled = false;
            console.log('UI updated after receiving data');

            // Render the analysis
            console.log('Rendering market analysis with data:', data);
            renderMarketAnalysis(data.result);
            console.log('Market analysis rendered successfully');
        })
        .catch(error => {
            console.error('Request failed:', error);
            
            // Hide loading state and show error
            document.getElementById('loadingState').classList.add('d-none');
            document.getElementById('analysisContent').classList.remove('d-none');
            document.getElementById('generateBtn').disabled = false;
            console.log('UI updated after error');
            
            showError('Error Generating Analysis',
                     'There was an error generating the market analysis. Please try again.',
                     error.message);
        });
    } catch (error) {
        console.error('Error in generateAnalysis function:', error);
        showError('Unexpected Error',
                 'An unexpected error occurred. Please try again.',
                 error.message);
    }
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
