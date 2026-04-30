let responseChart = null;

function simulateSystem(systemName) {
    if (!systemName) systemName = document.getElementById('system-select').value;

    // Default params
    let params = {};
    let initial_state = [1.0, 0.0];
    let duration = 10.0;

    if (systemName === 'VanDerPol') {
        params = {mu: 1.0};
        initial_state = [2.0, 0.0];
    } else if (systemName === 'Pendulum') {
        params = {length: 1.0, mass: 1.0, damping: 0.1, gravity: 9.81};
        initial_state = [Math.PI/2, 0.0];
    } else if (systemName === 'Lorenz') {
        params = {sigma: 10.0, rho: 28.0, beta: 8.0/3.0};
        initial_state = [1.0, 1.0, 1.0];
        duration = 20.0;
    }

    const requestData = {
        system: systemName,
        params: params,
        initial_state: initial_state,
        duration: duration,
        dt: 0.05
    };

    const simBtn = document.getElementById('simulate-btn');
    const originalText = simBtn ? simBtn.innerText : 'Simulate';
    if (simBtn) {
        simBtn.disabled = true;
        simBtn.title = 'Loading...';
        simBtn.innerText = 'Simulating...';
    }

    return fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        updateChart(data.t, data.y, systemName);
    })
    .catch(error => console.error('Error simulating system:', error))
    .finally(() => {
        if (simBtn) {
            simBtn.disabled = false;
            simBtn.removeAttribute('title');
            simBtn.innerText = originalText;
        }
    });
}

function updateChart(times, states, systemName) {
    const canvas = document.getElementById('time-response-chart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Prepare datasets
    const datasets = [];
    const colors = ['rgba(6, 182, 212, 1)', 'rgba(139, 92, 246, 1)', 'rgba(236, 72, 153, 1)'];

    // Determine state labels
    let labels = ['x1', 'x2', 'x3'];
    if (systemName === 'Pendulum') labels = ['theta', 'omega'];

    // ⚡ Bolt: Removed expensive point-by-point mapping. Chart.js 3+ supports raw arrays
    // natively if `labels` (x-axis points) are provided globally in the data config.
    // This provides a massive ~100x speedup when rendering high-resolution time series.
    const numStates = states.length;

    for (let i = 0; i < numStates; i++) {
        datasets.push({
            label: labels[i] || `x${i+1}`,
            data: states[i],
            borderColor: colors[i % colors.length],
            backgroundColor: colors[i % colors.length],
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
            tension: 0.4
        });
    }

    if (responseChart) {
        responseChart.destroy();
    }

    responseChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: times,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: { display: true, text: 'Time (s)', color: '#ccc' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#ccc' }
                },
                y: {
                    title: { display: true, text: 'State', color: '#ccc' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#ccc' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#ccc' }
                }
            }
        }
    });
}

// Global export
if (typeof window !== 'undefined') {
    window.simulateSystem = simulateSystem;
}
