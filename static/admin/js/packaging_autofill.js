/**
 * Iepakojuma šablona auto-fill
 * Kad admin produkta lapā izvēlas "Iepakojuma šablons" — automātiski
 * aizpilda svaru un izmērus, ja tie vēl nav ievadīti.
 */
(function() {
    'use strict';

    // Iegūst šablonu datus no lapas (ielikti no Django view)
    function getTemplates() {
        const el = document.getElementById('packaging-templates-data');
        if (el) {
            try { return JSON.parse(el.textContent); } catch(e) {}
        }
        // Fallback: mēģina no window
        return window.PACKAGING_TEMPLATES || [];
    }

    function handlePackagingChange(selectEl) {
        const templates = getTemplates();
        const selectedId = parseInt(selectEl.value);
        if (!selectedId) return;

        const tmpl = templates.find(t => t.id === selectedId);
        if (!tmpl) return;

        // Atrod vecāku rindu (inline tabulas rinda)
        const row = selectEl.closest('tr') || selectEl.closest('.inline-related');
        if (!row) return;

        const fields = {
            'weight_g':  tmpl.weight_g,
            'length_mm': tmpl.length_mm,
            'width_mm':  tmpl.width_mm,
            'height_mm': tmpl.height_mm,
        };

        Object.entries(fields).forEach(([fname, fval]) => {
            // Meklē input pēc name atribūta (Django inline nosaukums)
            const inputs = row.querySelectorAll('input[id*="' + fname + '"]');
            inputs.forEach(input => {
                // Aizpilda tikai ja tukšs
                if (!input.value) {
                    input.value = fval;
                    input.style.background = '#fffde7'; // dzeltens - auto-aizpildīts
                    input.title = 'Auto-aizpildīts no šablona: ' + tmpl.name;
                }
            });
        });

        // Parāda info paziņojumu
        let info = row.querySelector('.packaging-info');
        if (!info) {
            info = document.createElement('small');
            info.className = 'packaging-info text-success d-block mt-1';
            selectEl.parentNode.appendChild(info);
        }
        info.textContent = '✓ ' + tmpl.name + ': ' + tmpl.weight_g + 'g, '
            + tmpl.length_mm + '×' + tmpl.width_mm + '×' + tmpl.height_mm + 'mm';
    }

    function attachListeners() {
        // Pievieno klausītājus visiem esošajiem packaging dropdown
        document.querySelectorAll('select[id*="packaging"]').forEach(sel => {
            if (!sel.dataset.pfAttached) {
                sel.addEventListener('change', () => handlePackagingChange(sel));
                sel.dataset.pfAttached = '1';
                // Ja jau ir izvēlēts — rāda info
                if (sel.value) {
                    const templates = getTemplates();
                    const tmpl = templates.find(t => t.id === parseInt(sel.value));
                    if (tmpl) {
                        let info = sel.parentNode.querySelector('.packaging-info');
                        if (!info) {
                            info = document.createElement('small');
                            info.className = 'packaging-info text-muted d-block mt-1';
                            sel.parentNode.appendChild(info);
                        }
                        info.textContent = tmpl.weight_g + 'g, '
                            + tmpl.length_mm + '×' + tmpl.width_mm + '×' + tmpl.height_mm + 'mm';
                    }
                }
            }
        });
    }

    // MutationObserver — pievieno klausītājus arī jaunām inline rindām
    function observe() {
        const target = document.querySelector('#content-main') || document.body;
        const obs = new MutationObserver(() => attachListeners());
        obs.observe(target, { childList: true, subtree: true });
    }

    document.addEventListener('DOMContentLoaded', () => {
        attachListeners();
        observe();
    });
})();
