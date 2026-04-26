let scene, camera, renderer, currentMesh;
let isPausedByUser = false;
let needsRender = true;

function init3D(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.title = "Hover or focus to pause animation";
    container.addEventListener('mouseenter', () => { isPausedByUser = true; needsRender = true; });
    container.addEventListener('focus', () => { isPausedByUser = true; needsRender = true; });
    container.addEventListener('mouseleave', () => { isPausedByUser = false; needsRender = true; });
    container.addEventListener('blur', () => { isPausedByUser = false; needsRender = true; });

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

    // Handle resize
    window.addEventListener('resize', () => {
        if (!container) return;
        const width = container.clientWidth;
        const height = container.clientHeight;
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        needsRender = true;
    });
}

function update3D(systemName) {
    if (!systemName) systemName = document.getElementById('system-select')?.value || 'VanDerPol';

    if (currentMesh) {
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
const _origUpdatePhase = window.updatePhasePortrait;
window.updatePhasePortrait = function(sys) {
    let result;
    if (_origUpdatePhase) result = _origUpdatePhase(sys);
    update3D(sys);
    return result;
};

const _origSimulate = window.simulateSystem;
window.simulateSystem = function(sys) {
    let result;
    if (_origSimulate) result = _origSimulate(sys);
    update3D(sys);
    return result;
};

document.addEventListener('DOMContentLoaded', () => {
    init3D('3d-view');
});
