/**
 * theme.js — shared dark/light theme manager
 * Reads: localStorage 'cardio-theme' | system prefers-color-scheme
 * Writes: data-theme attribute on <html>
 */
(function () {
    const KEY = 'cardio-theme';

    function systemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        syncButton(theme);
    }

    function syncButton(theme) {
        const btn = document.getElementById('theme-toggle');
        if (!btn) return;
        const isDark = theme === 'dark';
        const sunEl  = btn.querySelector('.icon-sun');
        const moonEl = btn.querySelector('.icon-moon');
        if (sunEl)  sunEl.style.display  = isDark ? 'block' : 'none';
        if (moonEl) moonEl.style.display = isDark ? 'none'  : 'block';
        btn.setAttribute('title',      isDark ? 'Switch to light mode' : 'Switch to dark mode');
        btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    window.toggleTheme = function () {
        const current = document.documentElement.getAttribute('data-theme') || systemTheme();
        const next    = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(KEY, next);
        applyTheme(next);
    };

    // Apply immediately (before first paint, avoids FOUC)
    applyTheme(localStorage.getItem(KEY) || systemTheme());

    // Respect OS changes only when user has no saved preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!localStorage.getItem(KEY)) applyTheme(e.matches ? 'dark' : 'light');
    });

    document.addEventListener('DOMContentLoaded', function () {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            syncButton(document.documentElement.getAttribute('data-theme') || systemTheme());
            btn.addEventListener('click', window.toggleTheme);
        }
    });
})();
