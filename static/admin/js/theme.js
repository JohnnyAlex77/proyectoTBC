// static/admin/js/theme.js - ARCHIVO TEMPORAL
(function() {
    'use strict';
    
    // Función temporal para theme switching (si es necesario)
    window.addEventListener('load', function() {
        // Intentar cargar el tema guardado
        var theme = localStorage.getItem('adminTheme') || 'auto';
        applyTheme(theme);
        
        // Configurar listeners para switcher de tema si existe
        var themeSwitcher = document.querySelector('#theme-switcher');
        if (themeSwitcher) {
            themeSwitcher.addEventListener('change', function(e) {
                var selectedTheme = e.target.value;
                localStorage.setItem('adminTheme', selectedTheme);
                applyTheme(selectedTheme);
            });
        }
    });
    
    function applyTheme(theme) {
        var body = document.body;
        
        // Remover clases de tema anteriores
        body.classList.remove('theme-dark', 'theme-light', 'theme-auto');
        
        if (theme === 'dark') {
            body.classList.add('theme-dark');
        } else if (theme === 'light') {
            body.classList.add('theme-light');
        } else {
            body.classList.add('theme-auto');
            // Auto-detectar tema del sistema
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                body.classList.add('theme-dark');
            } else {
                body.classList.add('theme-light');
            }
        }
    }
    
    // Dark mode detection
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            var currentTheme = localStorage.getItem('adminTheme') || 'auto';
            if (currentTheme === 'auto') {
                applyTheme('auto');
            }
        });
    }
    
    console.log('Theme JS cargado - versión temporal');
})();