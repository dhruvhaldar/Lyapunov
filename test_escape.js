const fs = require('fs');
let code = fs.readFileSync('public/js/main.js', 'utf8');

const escapeCode = `
            // 🎨 Palette: Allow keyboard users to easily dismiss focus and tactile UI states using the Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && document.activeElement && document.activeElement !== document.body) {
                    document.activeElement.blur();
                }
            });
`;

code = code.replace('// Global keyboard shortcut', escapeCode + '\n            // Global keyboard shortcut');
fs.writeFileSync('public/js/main.js', code);
