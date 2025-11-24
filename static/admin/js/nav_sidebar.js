// static/admin/js/nav_sidebar.js - ARCHIVO TEMPORAL
(function() {
    'use strict';
    
    // Toggle functionality for sidebar
    function initSidebar() {
        var sidebar = document.getElementById('nav-sidebar');
        var toggle = document.getElementById('toggle-nav-sidebar');
        
        if (sidebar && toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                sidebar.classList.toggle('collapsed');
                
                // Guardar estado en localStorage
                var isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('django.admin.navSidebarIsCollapsed', isCollapsed);
                
                // Actualizar icono
                var icon = toggle.querySelector('i');
                if (icon) {
                    if (isCollapsed) {
                        icon.className = 'icon-arrow-right';
                    } else {
                        icon.className = 'icon-arrow-left';
                    }
                }
            });
            
            // Cargar estado guardado
            var savedState = localStorage.getItem('django.admin.navSidebarIsCollapsed');
            if (savedState === 'true') {
                sidebar.classList.add('collapsed');
            }
        }
    }
    
    // Sticky header functionality
    function initStickyHeader() {
        var header = document.querySelector('#header');
        var breadcrumbs = document.querySelector('.breadcrumbs');
        
        if (header && breadcrumbs) {
            window.addEventListener('scroll', function() {
                var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 50) {
                    header.classList.add('sticky');
                    if (breadcrumbs) {
                        breadcrumbs.style.paddingTop = header.offsetHeight + 'px';
                    }
                } else {
                    header.classList.remove('sticky');
                    if (breadcrumbs) {
                        breadcrumbs.style.paddingTop = '0';
                    }
                }
            });
        }
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initSidebar();
            initStickyHeader();
        });
    } else {
        initSidebar();
        initStickyHeader();
    }
    
    // Funciones globales para Django admin
    window.django = window.django || {};
    window.django.jQuery = window.django.jQuery || (function() {
        // Minimal jQuery compatibility layer
        return {
            ready: function(fn) {
                if (document.readyState !== 'loading') {
                    fn();
                } else {
                    document.addEventListener('DOMContentLoaded', fn);
                }
            },
            on: function(events, selector, handler) {
                document.addEventListener(events, function(e) {
                    if (e.target.matches(selector)) {
                        handler.call(e.target, e);
                    }
                });
            }
        };
    })();
    
    console.log('Nav Sidebar JS cargado - versión temporal');
})();