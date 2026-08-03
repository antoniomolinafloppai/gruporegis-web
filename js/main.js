(function () {
  'use strict';

  /* Footer year */
  var yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  /* Header scroll effect */
  var header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', function () {
      header.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  /* Mobile navigation */
  var navToggle = document.querySelector('.nav-toggle');
  var mainNav = document.getElementById('main-nav');

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      var expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
      mainNav.classList.toggle('open');
    });

    mainNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navToggle.setAttribute('aria-expanded', 'false');
        mainNav.classList.remove('open');
      });
    });
  }

  /* Cookie consent */
  var COOKIE_KEY = 'menhir_recycling_cookie_consent';
  var banner = document.getElementById('cookie-banner');
  var settingsPanel = document.getElementById('cookie-settings');
  var settingsToggle = document.getElementById('cookie-settings-toggle');

  function hideBanner() {
    if (banner) {
      banner.hidden = true;
    }
  }

  function saveConsent(value) {
    try {
      localStorage.setItem(COOKIE_KEY, value);
    } catch (e) {
      /* localStorage unavailable */
    }
    hideBanner();
  }

  if (banner) {
    var stored = null;
    try {
      stored = localStorage.getItem(COOKIE_KEY);
    } catch (e) {
      /* ignore */
    }

    if (!stored) {
      banner.hidden = false;
    }

    var acceptBtn = document.getElementById('cookie-accept');
    var necessaryBtn = document.getElementById('cookie-necessary');
    var saveBtn = document.getElementById('cookie-save');

    if (acceptBtn) {
      acceptBtn.addEventListener('click', function () {
        saveConsent('all');
      });
    }

    if (necessaryBtn) {
      necessaryBtn.addEventListener('click', function () {
        saveConsent('necessary');
      });
    }

    if (settingsToggle && settingsPanel) {
      settingsToggle.addEventListener('click', function () {
        var expanded = settingsToggle.getAttribute('aria-expanded') === 'true';
        settingsToggle.setAttribute('aria-expanded', String(!expanded));
        settingsPanel.hidden = expanded;
      });
    }

    if (saveBtn) {
      saveBtn.addEventListener('click', function () {
        saveConsent('custom');
      });
    }
  }
})();
