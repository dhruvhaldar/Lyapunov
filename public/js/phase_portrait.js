function updatePhasePortrait(systemName) {
    if (!systemName) systemName = document.getElementById('system-select').value;

    // Default params
    let params = {};
    if (systemName === 'VanDerPol') params = {mu: 1.0};
    if (systemName === 'Pendulum') params = {length: 1.0, mass: 1.0, damping: 0.1, gravity: 9.81};
    if (systemName === 'Lorenz') params = {sigma: 10.0, rho: 28.0, beta: 8.0/3.0};

    const requestData = {
        system: systemName,
        params: params,
        x_range: [-4, 4],
        y_range: [-4, 4]
    };

    if (systemName === 'Lorenz') {
        requestData.x_range = [-20, 20];
        requestData.y_range = [-30, 30];
    }

    const updateBtn = document.getElementById('update-phase');
    const originalText = updateBtn ? updateBtn.innerText : 'Update';
    if (updateBtn) {
        updateBtn.disabled = true;
        updateBtn.title = 'Loading...';
        updateBtn.innerText = 'Updating...';
    }

    return fetch('/api/phase_portrait', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        // ⚡ Bolt: Remap Structure of Arrays (SoA) payload back to Array of Structures
        // to maintain d3 rendering compatibility, executing rapidly on the client side.
        // Pre-calculate algebraic offsets (dx, dy) to avoid slow trig (atan2, cos, sin) per-vector during rendering
        const vectorsArray = data.vectors.x.map((x, i) => {
            const u = data.vectors.u[i];
            const v = data.vectors.v[i];
            const mag = Math.sqrt(u*u + v*v);
            const len = 10;
            return {
                x: x,
                y: data.vectors.y[i],
                u: u,
                v: v,
                mag: mag,
                dx: mag >= 1e-6 ? (u / mag) * len : 0,
                dy: mag >= 1e-6 ? (v / mag) * len : 0
            };
        });
        drawPhasePortrait(vectorsArray, systemName);
    })
    .catch(error => {
        console.error('Error fetching phase portrait:', error);
        throw error;
    })
    .finally(() => {
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.removeAttribute('title');
            updateBtn.innerText = originalText;
        }
    });
}

function drawPhasePortrait(vectors, systemName) {
    const container = document.getElementById('phase-portrait');
    container.innerHTML = '';

    const width = container.clientWidth || 400;
    const height = container.clientHeight || 400;

    const svg = d3.select("#phase-portrait")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Add arrow marker
    svg.append("defs").append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 8)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#00ffcc");

    const xExtent = d3.extent(vectors, d => d.x);
    const yExtent = d3.extent(vectors, d => d.y);

    const padding = 20;

    const xScale = d3.scaleLinear()
        .domain(xExtent)
        .range([padding, width - padding]);

    const yScale = d3.scaleLinear()
        .domain(yExtent)
        .range([height - padding, padding]);

    const lines = svg.selectAll("line")
        .data(vectors)
        .enter()
        .append("line")
        .attr("class", "vector-line")
        .attr("x1", d => xScale(d.x))
        .attr("y1", d => yScale(d.y))
        .attr("x2", d => xScale(d.x) + d.dx)
        .attr("y2", d => yScale(d.y) - d.dy)
        .attr("stroke", "rgba(0, 255, 204, 0.6)")
        .attr("stroke-width", 1.5)
        .attr("marker-end", "url(#arrow)");

    lines.append("title")
        .text(d => `Position: (${d.x.toFixed(2)}, ${d.y.toFixed(2)})\nVector: (${d.u.toFixed(2)}, ${d.v.toFixed(2)})\nMagnitude: ${d.mag.toFixed(2)}`);

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(5);
    const yAxis = d3.axisLeft(yScale).ticks(5);

    const xZero = xScale(0);
    const yZero = yScale(0);

    svg.append("g")
        .attr("transform", `translate(0, ${yZero})`)
        .call(xAxis)
        .attr("color", "#ccc")
        .style("font-family", "inherit")
        .select(".domain").remove();

    svg.append("g")
        .attr("transform", `translate(${xZero}, 0)`)
        .call(yAxis)
        .attr("color", "#ccc")
        .style("font-family", "inherit")
        .select(".domain").remove();

    // Contextual Labels
    let xLabel = 'x1', yLabel = 'x2';
    if (systemName === 'Pendulum') { xLabel = 'θ'; yLabel = 'ω'; }
    if (systemName === 'Lorenz') { xLabel = 'x'; yLabel = 'y'; }

    svg.append("text")
        .attr("x", width - 10)
        .attr("y", yZero - 10)
        .attr("fill", "#ccc")
        .style("font-family", "inherit")
        .style("font-size", "12px")
        .text(xLabel);

    svg.append("text")
        .attr("x", xZero + 10)
        .attr("y", 20)
        .attr("fill", "#ccc")
        .style("font-family", "inherit")
        .style("font-size", "12px")
        .text(yLabel);
}

// Make globally available
if (typeof window !== 'undefined') {
    window.updatePhasePortrait = updatePhasePortrait;
}
