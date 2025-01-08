function renderMarketAnalysis(data) {
    console.log('Starting renderMarketAnalysis with data:', data);
    const container = document.getElementById('marketAnalysisData');
    if (!container) {
        console.error('marketAnalysisData container not found');
        return;
    }

    try {
        // Convert markdown to HTML
        const converter = new showdown.Converter();
        const html = converter.makeHtml(data);
        console.log('Converted markdown to HTML');
        
        // Add Bootstrap classes to elements
        const styledHtml = html
            .replace(/<h1/g, '<h1 class="mb-4 fw-bold"')
            .replace(/<h2/g, '<h2 class="mt-4 mb-3 fw-semibold"')
            .replace(/<ul/g, '<ul class="list-unstyled ps-3"')
            .replace(/<li/g, '<li class="mb-2 text-gray-800"');

        container.innerHTML = `
            <div class="market-analysis-content card">
                <div class="card-body">
                    ${styledHtml}
                </div>
            </div>
        `;
        console.log('Rendered styled HTML content');
    } catch (error) {
        console.error('Error rendering market analysis:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <h4 class="alert-heading">Error Rendering Analysis</h4>
                <p>There was an error rendering the market analysis data. Please try generating the analysis again.</p>
                <hr>
                <p class="mb-0">Error details: ${error.message}</p>
            </div>
        `;
    }
}
