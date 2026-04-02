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
        updateBtn.innerText = 'Updating...';
    }

    return fetch('/api/phase_portrait', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        // ⚡ Bolt: Remap Structure of Arrays (SoA) payload back to Array of Structures
        // to maintain d3 rendering compatibility, executing rapidly on the client side.
        const vectorsArray = data.vectors.x.map((x, i) => ({
            x: x,
            y: data.vectors.y[i],
            u: data.vectors.u[i],
            v: data.vectors.v[i]
        }));
        drawPhasePortrait(vectorsArray);
    })
    .catch(error => console.error('Error fetching phase portrait:', error))
    .finally(() => {
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.innerText = originalText;
        }
    });
}

function drawPhasePortrait(vectors) {
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

    svg.selectAll("line")
        .data(vectors)
        .enter()
        .append("line")
        .attr("x1", d => xScale(d.x))
        .attr("y1", d => yScale(d.y))
        .attr("x2", d => {
            const mag = Math.sqrt(d.u*d.u + d.v*d.v);
            if (mag < 1e-6) return xScale(d.x);
            // Draw a small vector of fixed pixel length to show direction
            const len = 10;
            const angle = Math.atan2(d.v, d.u);
            return xScale(d.x) + Math.cos(angle) * len;
        })
        .attr("y2", d => {
            const mag = Math.sqrt(d.u*d.u + d.v*d.v);
             if (mag < 1e-6) return yScale(d.y);
             const len = 10;
             const angle = Math.atan2(d.v, d.u);
             // SVG y is down, so minus sin(angle) effectively, but yScale handles coordinate mapping?
             // No, yScale maps the point. For the offset, we operate in pixel space.
             // In pixel space, y increases downwards.
             // atan2(v, u) gives standard math angle (CCW from +x).
             // If v is positive, angle is > 0. Math y goes up.
             // We want pixel y to go up (which is smaller value).
             // So we need to subtract sin(angle) * len.
             return yScale(d.y) - Math.sin(angle) * len;
        })
        .attr("stroke", "rgba(0, 255, 204, 0.6)")
        .attr("stroke-width", 1.5)
        .attr("marker-end", "url(#arrow)");

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(5);
    const yAxis = d3.axisLeft(yScale).ticks(5);

    const xZero = xScale(0);
    const yZero = yScale(0);

    svg.append("g")
        .attr("transform", `translate(0, ${yZero})`)
        .call(xAxis)
        .attr("color", "rgba(255,255,255,0.5)")
        .select(".domain").remove();

    svg.append("g")
        .attr("transform", `translate(${xZero}, 0)`)
        .call(yAxis)
        .attr("color", "rgba(255,255,255,0.5)")
        .select(".domain").remove();
}

// Make globally available
if (typeof window !== 'undefined') {
    window.updatePhasePortrait = updatePhasePortrait;
}
