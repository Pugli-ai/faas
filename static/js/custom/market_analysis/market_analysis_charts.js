let marketCharts = {};

function createMarketSizeChart(data) {
    try {
        console.log('Creating market size chart with data:', data);
        const ctx = document.getElementById('marketSizeChart').getContext('2d');
        const currentSize = formatNumber(data.market_size_and_growth.current_size);
        const growthProjections = formatNumber(data.market_size_and_growth.growth_projections);
        
        console.log('Market Size Chart Data:', { currentSize, growthProjections });
        
        marketCharts.sizeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Current Size', 'Growth Rate'],
                datasets: [{
                    label: 'Market Metrics',
                    data: [currentSize, growthProjections],
                    backgroundColor: ['rgba(54, 153, 255, 0.5)', 'rgba(75, 192, 192, 0.5)'],
                    borderColor: ['rgb(54, 153, 255)', 'rgb(75, 192, 192)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Market Size and Growth Rate'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                const dataIndex = context.dataIndex;
                                if (dataIndex === 0) {
                                    return `Market Size: ${formatCurrency(value)}`;
                                } else {
                                    return `Growth Rate: ${value}%`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value, index, values) {
                                if (index === 0) {
                                    return formatCurrency(value);
                                }
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating market size chart:', error);
        document.getElementById('marketSizeChart').parentElement.innerHTML = 
            '<div class="alert alert-warning">Unable to create market size chart due to data format issues.</div>';
    }
}

function createSegmentsChart(data) {
    try {
        console.log('Creating segments chart with data:', data);
        const ctx = document.getElementById('segmentsChart').getContext('2d');
        const segments = data.market_segments.segments;
        const growthPotential = data.market_segments.growth_potential;
        
        // Ensure we have valid data
        if (!segments || !growthPotential || !Array.isArray(segments)) {
            throw new Error('Invalid segments data structure');
        }
        
        const growth = segments.map(segment => formatNumber(growthPotential[segment]));
        console.log('Segments Chart Data:', { segments, growth });
        
        marketCharts.segmentsChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: segments,
                datasets: [{
                    label: 'Growth Potential (%)',
                    data: growth,
                    fill: true,
                    backgroundColor: 'rgba(54, 153, 255, 0.2)',
                    borderColor: 'rgb(54, 153, 255)',
                    pointBackgroundColor: 'rgb(54, 153, 255)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 153, 255)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Market Segments Growth Potential'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Growth: ${context.raw}%`;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating segments chart:', error);
        document.getElementById('segmentsChart').parentElement.innerHTML = 
            '<div class="alert alert-warning">Unable to create segments chart due to data format issues.</div>';
    }
}

function destroyCharts() {
    Object.values(marketCharts).forEach(chart => {
        try {
            chart.destroy();
        } catch (error) {
            console.error('Error destroying chart:', error);
        }
    });
    marketCharts = {};
}
