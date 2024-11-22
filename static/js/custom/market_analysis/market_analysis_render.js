function renderMarketAnalysis(data) {
    console.log('Starting renderMarketAnalysis with data:', data);
    const container = document.getElementById('marketAnalysisData');
    if (!container) {
        console.error('marketAnalysisData container not found');
        return;
    }
    let html = '';

    try {
        // Validate data structure
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid data format');
        }

        console.log('Data validation passed, proceeding with render');

        // Market Size and Growth Section with Chart
        if (data.market_size_and_growth) {
            html += `
                <div class="market-section">
                    <h3><i class="fas fa-chart-line"></i>Market Size and Growth</h3>
                    <div class="market-grid">
                        <div class="market-stat-card">
                            <h4>Current Market Size</h4>
                            <div class="stat-value">${formatCurrency(data.market_size_and_growth.current_size)}</div>
                        </div>
                        <div class="market-stat-card">
                            <h4>Growth Projections</h4>
                            <div class="stat-value">${data.market_size_and_growth.growth_projections}%</div>
                        </div>
                    </div>
                    <div class="market-chart-container">
                        <canvas id="marketSizeChart"></canvas>
                    </div>
                    <h4><i class="fas fa-rocket"></i>Key Growth Drivers</h4>
                    <div class="market-data-list">
                        ${Array.isArray(data.market_size_and_growth.key_drivers) ? 
                            data.market_size_and_growth.key_drivers.map(driver => `
                                <div class="market-list-item">
                                    <i class="fas fa-chevron-right"></i>
                                    <span>${driver}</span>
                                </div>
                            `).join('') : 
                            '<div class="alert alert-warning">No growth drivers data available</div>'
                        }
                    </div>
                </div>
            `;
        }

        // Market Segments Section with Chart
        if (data.market_segments && Array.isArray(data.market_segments.segments)) {
            html += `
                <div class="market-section">
                    <h3><i class="fas fa-puzzle-piece"></i>Market Segments</h3>
                    <div class="market-chart-container">
                        <canvas id="segmentsChart"></canvas>
                    </div>
                    <h4><i class="fas fa-chart-pie"></i>Segments</h4>
                    <div class="market-data-list mb-4">
                        ${data.market_segments.segments.map(segment => `
                            <div class="market-list-item">
                                <i class="fas fa-check-circle"></i>
                                <span>${segment}</span>
                            </div>
                        `).join('')}
                    </div>
                    <h4><i class="fas fa-chart-bar"></i>Growth Potential by Segment</h4>
                    <ul class="market-data-list">
                        ${Object.entries(data.market_segments.growth_potential || {}).map(([segment, potential]) => `
                            <li><span class="market-metric">${segment}:</span> <span class="market-value">${potential}%</span></li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        // Market Trends Section
        if (data.market_trends) {
            html += `
                <div class="market-section">
                    <h3><i class="fas fa-chart-bar"></i>Market Trends</h3>
                    <h4><i class="fas fa-trending-up"></i>Current Trends</h4>
                    <div class="market-data-list mb-4">
                        ${Array.isArray(data.market_trends.current_trends) ?
                            data.market_trends.current_trends.map(trend => `
                                <div class="market-list-item">
                                    <i class="fas fa-arrow-trend-up"></i>
                                    <span>${trend}</span>
                                </div>
                            `).join('') :
                            '<div class="alert alert-warning">No current trends data available</div>'
                        }
                    </div>
                    <h4><i class="fas fa-lightbulb"></i>Emerging Opportunities</h4>
                    <div class="market-data-list">
                        ${Array.isArray(data.market_trends.emerging_opportunities) ?
                            data.market_trends.emerging_opportunities.map(opportunity => `
                                <div class="market-list-item">
                                    <i class="fas fa-star"></i>
                                    <span>${opportunity}</span>
                                </div>
                            `).join('') :
                            '<div class="alert alert-warning">No emerging opportunities data available</div>'
                        }
                    </div>
                </div>
            `;
        }

        // Market Challenges Section
        if (data.market_challenges) {
            html += `
                <div class="market-section">
                    <h3><i class="fas fa-exclamation-triangle"></i>Market Challenges</h3>
                    <h4><i class="fas fa-ban"></i>Entry Barriers</h4>
                    <div class="market-data-list mb-4">
                        ${Array.isArray(data.market_challenges.entry_barriers) ?
                            data.market_challenges.entry_barriers.map(barrier => `
                                <div class="market-list-item">
                                    <i class="fas fa-shield-alt"></i>
                                    <span>${barrier}</span>
                                </div>
                            `).join('') :
                            '<div class="alert alert-warning">No entry barriers data available</div>'
                        }
                    </div>
                    <h4><i class="fas fa-gavel"></i>Regulatory Challenges</h4>
                    <div class="market-data-list mb-4">
                        ${Array.isArray(data.market_challenges.regulatory_challenges) ?
                            data.market_challenges.regulatory_challenges.map(challenge => `
                                <div class="market-list-item">
                                    <i class="fas fa-balance-scale"></i>
                                    <span>${challenge}</span>
                                </div>
                            `).join('') :
                            '<div class="alert alert-warning">No regulatory challenges data available</div>'
                        }
                    </div>
                    <h4><i class="fas fa-exclamation-circle"></i>Market Risks</h4>
                    <div class="market-data-list">
                        ${Array.isArray(data.market_challenges.risks) ?
                            data.market_challenges.risks.map(risk => `
                                <div class="market-list-item">
                                    <i class="fas fa-exclamation"></i>
                                    <span>${risk}</span>
                                </div>
                            `).join('') :
                            '<div class="alert alert-warning">No market risks data available</div>'
                        }
                    </div>
                </div>
            `;
        }

        console.log('Generated HTML:', html);
        container.innerHTML = html;

        console.log('HTML inserted, initializing charts');
        // Initialize charts after DOM is updated
        if (data.market_size_and_growth) {
            createMarketSizeChart(data);
        }
        if (data.market_segments) {
            createSegmentsChart(data);
        }
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
