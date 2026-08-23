let scene, camera, renderer, currentMesh;
let isHovered = false;
let isFocused = false;
let isTouched = false;
let isPausedByUser = false;
let needsRender = true;
let _prevPausedByUser = false;

function updatePauseState() {
    isPausedByUser = isHovered || isFocused || isTouched;
    needsRender = true;

    // Check if we should pause due to user preference OR interaction
    const isPaused = isPausedByUser || prefersReducedMotion;

    // 🎨 Palette: Sync visual feedback class to ensure consistency across all input modalities (hover, focus, touch, reduced motion)
    const container = document.getElementById('3d-view');
    if (container) {
        if (isPaused) {
            container.classList.add('is-paused');
            const badge = container.querySelector('.paused-badge');
            if (badge) {
                // If paused due to reduced motion preference and not actively interacted with
                if (prefersReducedMotion && !isPausedByUser) {
                    badge.textContent = '⏸ Reduced Motion';
                } else {
                    badge.textContent = '⏸ Paused';
                }
            }
        } else {
            container.classList.remove('is-paused');
        }
    }

    // 🎨 Palette: Provide explicit auditory feedback when the pause state changes
    if (isPaused !== _prevPausedByUser) {
        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            if (isPaused) {
                announcer.textContent = (prefersReducedMotion && !isPausedByUser) ? '3D Animation reduced motion.' : '3D Animation paused.';
            } else {
                announcer.textContent = '3D Animation resumed.';
            }
        }
        _prevPausedByUser = isPaused;
    }
}

function init3D(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.title = "Hover, focus, or touch to pause animation";
    container.addEventListener('mouseenter', () => { isHovered = true; updatePauseState(); });
    container.addEventListener('mouseleave', () => { isHovered = false; updatePauseState(); });
    container.addEventListener('focus', () => { isFocused = true; updatePauseState(); });
    container.addEventListener('blur', () => { isFocused = false; updatePauseState(); });
    container.addEventListener('touchstart', (e) => { isTouched = true; updatePauseState(); });
    container.addEventListener('touchend', (e) => { isTouched = false; updatePauseState(); });
    container.addEventListener('touchcancel', (e) => { isTouched = false; updatePauseState(); });

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);

    camera.position.z = 30;

    // Initial load
    update3D('VanDerPol');

    animate();

    // Ensure initial state handles prefersReducedMotion correctly
    updatePauseState();

    // Handle resize
    let resizeScheduled = false;
    window.addEventListener('resize', () => {
        if (!container || resizeScheduled) return;
        resizeScheduled = true;
        requestAnimationFrame(() => {
            const width = container.clientWidth;
            const height = container.clientHeight;
            renderer.setSize(width, height);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            needsRender = true;
            resizeScheduled = false;
        });
    });
}

function update3D(systemName) {
    if (!systemName) systemName = document.getElementById('system-select')?.value || 'VanDerPol';

    if (currentMesh) {
        // ⚡ Bolt: Explicitly dispose of WebGL buffers when removing meshes to prevent memory leaks
        currentMesh.traverse((node) => {
            if (node.isMesh || node.isLine) {
                if (node.geometry) node.geometry.dispose();
                if (node.material) {
                    if (Array.isArray(node.material)) {
                        node.material.forEach(mat => mat.dispose());
                    } else {
                        node.material.dispose();
                    }
                }
            }
        });
        scene.remove(currentMesh);
    }

    if (systemName === 'Lorenz') {
        // Create a particle system for Lorenz
        // ⚡ Bolt: Replaced iterative THREE.Vector3 object allocation with a pre-allocated Float32Array
        // to prevent large garbage collection (GC) pauses and improve geometry initialization speed.
        const numPoints = 3000;
        const positions = new Float32Array(numPoints * 3);
        let x = 0.1, y = 0, z = 0;
        const sigma = 10, rho = 28, beta = 8/3;
        const dt = 0.01;
        for (let i = 0; i < numPoints; i++) {
            const dx = sigma * (y - x);
            const dy = x * (rho - z) - y;
            const dz = x * y - beta * z;
            x += dx * dt;
            y += dy * dt;
            z += dz * dt;

            const idx = i * 3;
            positions[idx] = x;
            positions[idx + 1] = y;
            positions[idx + 2] = z;
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const material = new THREE.LineBasicMaterial({ color: 0x00ffcc });
        currentMesh = new THREE.Line(geometry, material);
        // Center it roughly
        currentMesh.position.y = -20;

    } else if (systemName === 'Pendulum') {
        // Simple pendulum representation
        const group = new THREE.Group();

        // Pivot
        const pivotGeo = new THREE.SphereGeometry(0.5);
        const pivotMat = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });
        const pivot = new THREE.Mesh(pivotGeo, pivotMat);
        group.add(pivot);

        // Arm
        const armGeo = new THREE.CylinderGeometry(0.1, 0.1, 5);
        const armMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
        const arm = new THREE.Mesh(armGeo, armMat);
        arm.position.y = -2.5;
        group.add(arm);

        // Bob
        const bobGeo = new THREE.SphereGeometry(1);
        const bobMat = new THREE.MeshStandardMaterial({ color: 0xff0066 });
        const bob = new THREE.Mesh(bobGeo, bobMat);
        bob.position.y = -5;
        group.add(bob);

        currentMesh = group;
        currentMesh.scale.set(2, 2, 2);

    } else {
        // Default (VanDerPol) - Visualized as a Torus Knot?
        // Or just a sphere
        const geometry = new THREE.TorusKnotGeometry( 6, 2, 100, 16 );
        const material = new THREE.MeshPhongMaterial( { color: 0x8b5cf6, wireframe: true } );
        currentMesh = new THREE.Mesh( geometry, material );
    }

    scene.add(currentMesh);
    needsRender = true;
}

// ⚡ Bolt: Cache media query outside of animation loop to prevent synchronous string parsing 60fps
const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
let prefersReducedMotion = reducedMotionQuery.matches;
reducedMotionQuery.addEventListener('change', (e) => {
    prefersReducedMotion = e.matches;
    updatePauseState();
});

function animate() {
    requestAnimationFrame(animate);

    // ⚡ Bolt: Skip expensive WebGL rendering when the scene is static
    // (either due to user pause or reduced motion preference) to save battery and GPU cycles.
    let isAnimating = currentMesh && !prefersReducedMotion && !isPausedByUser;

    if (isAnimating) {
        currentMesh.rotation.y += 0.01;
        if (currentMesh.type === 'Line') {
             currentMesh.rotation.z += 0.005;
        }
        needsRender = true;
    }

    if (needsRender) {
        renderer.render(scene, camera);
        if (!isAnimating) {
            needsRender = false;
        }
    }
}

// Hook into global functions to update 3D when system changes
// We'll wrap the existing functions if they exist
// ⚡ Bolt: Debounce the update3D calls so that when main.js triggers both
// phase portrait and time response simulation concurrently via Promise.all,
// we only tear down and recreate the WebGL geometry once per tick.
let update3DTimeout = null;
const debouncedUpdate3D = (sys) => {
    if (update3DTimeout) clearTimeout(update3DTimeout);
    update3DTimeout = setTimeout(() => {
        update3D(sys);
        update3DTimeout = null;
    }, 10);
};

const _origUpdatePhase = window.updatePhasePortrait;
window.updatePhasePortrait = function(sys) {
    let result;
    if (_origUpdatePhase) result = _origUpdatePhase(sys);
    debouncedUpdate3D(sys);
    return result;
};

const _origSimulate = window.simulateSystem;
window.simulateSystem = function(sys) {
    let result;
    if (_origSimulate) result = _origSimulate(sys);
    debouncedUpdate3D(sys);
    return result;
};

document.addEventListener('DOMContentLoaded', () => {
    init3D('3d-view');
});
