        // Main initialization
        document.addEventListener('DOMContentLoaded', () => {
            const systemSelect = document.getElementById('system-select');

            // Add a visually hidden element for a11y announcements
            const announcer = document.getElementById('a11y-announcer');

            function syncContextLabels() {
                const originalText = systemSelect.options[systemSelect.selectedIndex].text;
                document.getElementById('heading-phase').textContent = `Phase Portrait: ${originalText}`;
                document.getElementById('heading-time').textContent = `Time Response: ${originalText}`;
                document.getElementById('heading-3d').textContent = `3D Visualization: ${originalText}`;

                const phaseContainer = document.getElementById('phase-portrait');
                if (phaseContainer) phaseContainer.setAttribute('aria-label', `Interactive phase portrait showing system trajectories and vector fields for ${originalText}`);

                const timeContainer = document.getElementById('time-response-chart');
                if (timeContainer) timeContainer.setAttribute('aria-label', `Interactive time response chart showing system states over time for ${originalText}`);

                const view3dContainer = document.getElementById('3d-view');
                if (view3dContainer) view3dContainer.setAttribute('aria-label', `Interactive 3D visualization of the ${originalText} dynamical system. Focus to pause animation.`);

                document.title = `Lyapunov Control Dashboard - ${originalText}`;
            }

            const refreshBtn = document.getElementById('refresh-btn');

            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    if (refreshBtn.getAttribute('aria-disabled') === 'true') return;
                    systemSelect.dispatchEvent(new Event('change'));
                });
            }

            // Read hash to initialize previousValue correctly before the change event listener is attached
            const initialHash = window.location.hash.substring(1);
            if (initialHash && Array.from(systemSelect.options).some(opt => opt.value === initialHash)) {
                systemSelect.value = initialHash;
            }

            let previousValue = systemSelect.value;

            systemSelect.addEventListener('change', () => {
                if (systemSelect.getAttribute('aria-disabled') === 'true') {
                    systemSelect.value = previousValue; // Revert visually to prevent confusion
                    return;
                }
                const sys = systemSelect.value;
                const originalText = systemSelect.options[systemSelect.selectedIndex].text;
                const mainContent = document.querySelector('main');

                syncContextLabels();

                // Remember focus state to restore it after loading
                const hadFocus = document.activeElement === systemSelect;
                const refreshHadFocus = document.activeElement === refreshBtn;

                // Set loading state
                systemSelect.setAttribute('aria-disabled', 'true');
                systemSelect.title = "Loading...";

                if (refreshBtn) {
                    refreshBtn.setAttribute('aria-disabled', 'true');
                    refreshBtn.title = "Loading...";
                    const svg = refreshBtn.querySelector('svg');
                    if (svg) svg.classList.add('spin-icon');
                }

                announcer.textContent = `Loading system ${originalText}...`;

                if (mainContent) {
                    mainContent.setAttribute('aria-busy', 'true');
                }

                const promises = [];
                if (window.updatePhasePortrait) {
                    promises.push(window.updatePhasePortrait(sys));
                }
                if (window.simulateSystem) {
                    promises.push(window.simulateSystem(sys));
                }

                Promise.all(promises).then(() => {
                    // Announce success
                    announcer.textContent = `System ${originalText} loaded successfully.`;
                    previousValue = sys;
                    window.history.replaceState(null, null, '#' + sys);
                }).catch(error => {
                    announcer.textContent = `Error loading system ${originalText}.`;

                    // 🎨 Palette: Revert UI state on failure to prevent misleading data visualization mismatches
                    if (systemSelect.value !== previousValue) {
                        systemSelect.value = previousValue;
                        syncContextLabels();
                        // Revert visualizations back to previous valid state
                        if (window.updatePhasePortrait) window.updatePhasePortrait(previousValue);
                        if (window.simulateSystem) window.simulateSystem(previousValue);
                    }

                    // Visual error feedback for sighted users
                    const toast = document.createElement('div');
                    toast.className = 'glass-panel';
                    toast.textContent = `⚠️ Error loading ${originalText}. Please try again.`;
                    toast.setAttribute('aria-hidden', 'true');
                    Object.assign(toast.style, {
                        position: 'fixed', bottom: '24px', right: '24px',
                        borderLeft: '4px solid #ef4444', padding: '16px 24px',
                        zIndex: '1000', opacity: '0', transform: 'translateY(10px)',
                        transition: 'all 0.3s ease'
                    });
                    document.body.appendChild(toast);
                    requestAnimationFrame(() => {
                        toast.style.opacity = '1';
                        toast.style.transform = 'translateY(0)';
                    });
                    setTimeout(() => {
                        toast.style.opacity = '0';
                        toast.style.transform = 'translateY(10px)';
                        setTimeout(() => toast.remove(), 300);
                    }, 5000);
                }).finally(() => {
                    // Restore state
                    systemSelect.removeAttribute('aria-disabled');
                    systemSelect.removeAttribute('title');

                    if (refreshBtn) {
                        refreshBtn.removeAttribute('aria-disabled');
                        refreshBtn.title = "Restart simulation (R)";
                        const svg = refreshBtn.querySelector('svg');
                        if (svg) svg.classList.remove('spin-icon');
                    }

                    if (mainContent) {
                        mainContent.removeAttribute('aria-busy');
                    }
                    // Restore focus if the user was interacting with it
                    if (hadFocus) {
                        systemSelect.focus();
                    } else if (refreshHadFocus && refreshBtn) {
                        refreshBtn.focus();
                    }
                });
            });

            syncContextLabels();

            // Prevent interaction with disabled elements when pointer-events is active
            document.addEventListener('click', (e) => {
                if (e.target.closest('[aria-disabled="true"]')) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, true);

            document.addEventListener('mousedown', (e) => {
                if (e.target.closest('[aria-disabled="true"]')) {
                    e.preventDefault(); // Prevents select dropdowns from opening natively on mousedown
                }
            }, true);

            document.addEventListener('keydown', (e) => {
                if (e.target.closest('[aria-disabled="true"]')) {
                    const interactionKeys = ['Enter', ' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
                    if (interactionKeys.includes(e.key)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            }, true);

            // Global keyboard shortcut
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey || e.metaKey || e.altKey) return; // Prevent hijacking native browser shortcuts like Save (Ctrl+S) or Reload (Ctrl+R)

                if (e.key.toLowerCase() === 's' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA' && document.activeElement.tagName !== 'SELECT') {
                    e.preventDefault();
                    systemSelect.focus();

                    // Tactile visual feedback
                    const kbd = document.getElementById('kbd-s');
                    if (kbd) {
                        kbd.classList.add('kbd-active');
                        setTimeout(() => {
                            kbd.classList.remove('kbd-active');
                        }, 150);
                    }
                }

                if (e.key.toLowerCase() === 'r' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA' && document.activeElement.tagName !== 'SELECT') {
                    e.preventDefault();
                    if (refreshBtn && refreshBtn.getAttribute('aria-disabled') !== 'true') {
                        refreshBtn.focus();
                        refreshBtn.click();

                        // Tactile visual feedback
                        const kbd = document.getElementById('kbd-r');
                        if (kbd) {
                            kbd.classList.add('kbd-active');
                            setTimeout(() => {
                                kbd.classList.remove('kbd-active');
                            }, 150);
                        }
                    }
                }
            });

            // Initial load (trigger change event to ensure loading states and spinners are shown)
            systemSelect.dispatchEvent(new Event('change'));
        });
