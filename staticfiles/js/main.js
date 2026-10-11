/* ============================================================================
   Beginners Hut — site behaviour
   ----------------------------------------------------------------------------
   Sections:
     1. Lenis smooth scroll      (single instance, owns the RAF loop)
     2. Navbar scroll state
     3. Active section tracking
     4. Mobile menu
     5. Theme toggle
     6. Portfolio filters + load more
     7. Animated counters
     8. Scroll reveal
     9. Go to top
    10. Flash messages
    11. Third-party guards (Swiper / Lightbox)
   ========================================================================== */

(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ==========================================================================
     1. LENIS SMOOTH SCROLL
     One instance only. Previously Lenis was constructed twice (inline script
     + main.js), which ran two rAF loops and caused visible jitter.
     ========================================================================== */

  var lenis = null;

  if (typeof window.Lenis !== 'undefined' && !reducedMotion) {
    lenis = new window.Lenis({
      lerp: 0.09,          // lower = smoother / more inertia
      wheelMultiplier: 1,
      touchMultiplier: 1.6,
      smoothWheel: true,
      syncTouch: false
    });

    function raf(time) {
      lenis.raf(time);
      window.requestAnimationFrame(raf);
    }
    window.requestAnimationFrame(raf);

    // Expose for other scripts / debugging
    window.bhLenis = lenis;
  }

  /* Scroll offset that clears the fixed navbar */
  var NAV_OFFSET = -100;

  function scrollToTarget(target) {
    if (!target) return;
    if (lenis) {
      lenis.scrollTo(target, { offset: NAV_OFFSET, duration: 1.15 });
    } else {
      var top = target.getBoundingClientRect().top + window.pageYOffset;
      window.scrollTo({ top: top - 100, behavior: reducedMotion ? 'auto' : 'smooth' });
    }
  }

  /* ==========================================================================
     2. NAVBAR SCROLL STATE
     ========================================================================== */

  var nav = document.querySelector('[data-bh-nav]');
  var navTicking = false;

  function updateNav() {
    navTicking = false;
    if (!nav) return;
    var y = lenis ? lenis.scroll : window.pageYOffset;
    nav.classList.toggle('is-scrolled', y > 24);
  }

  function onNavScroll() {
    if (navTicking) return;
    navTicking = true;
    window.requestAnimationFrame(updateNav);
  }

  if (lenis) {
    lenis.on('scroll', onNavScroll);
  } else {
    window.addEventListener('scroll', onNavScroll, { passive: true });
  }
  updateNav();

  /* ==========================================================================
     3. ACTIVE SECTION TRACKING
     Highlights the nav link whose section is currently on screen.
     ========================================================================== */

  (function activeSections() {
    var links = Array.prototype.slice.call(document.querySelectorAll('[data-bh-navlink]'));
    if (!links.length || !('IntersectionObserver' in window)) return;

    // Map "#id" -> matching link
    var byHash = {};
    links.forEach(function (a) {
      var hash = a.getAttribute('href') || '';
      var idx = hash.indexOf('#');
      if (idx > -1) {
        var id = hash.slice(idx + 1);
        if (id && !byHash[id]) byHash[id] = a;
      }
    });

    var ids = Object.keys(byHash);

    /* Links that point at a real page (Portfolio -> /portfolio/) carry no hash
       to track, so they are matched on pathname instead. */
    var byPath = {};
    links.forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (!href || href.indexOf('#') > -1) return;
      byPath[new URL(a.href, window.location.href).pathname] = a;
    });

    var pageLink = byPath[window.location.pathname] || null;

    if (!ids.length && !pageLink) return;
    if (!ids.length) {
      pageLink.classList.add('is-active');
      return;
    }

    var visible = {};

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });

      // Pick the most visible section
      var bestId = null;
      var bestRatio = 0;
      Object.keys(visible).forEach(function (id) {
        if (visible[id] > bestRatio) {
          bestRatio = visible[id];
          bestId = id;
        }
      });

      links.forEach(function (a) { a.classList.remove('is-active'); });
      if (bestId) byHash[bestId].classList.add('is-active');
      else if (pageLink) pageLink.classList.add('is-active');
    }, {
      rootMargin: '-45% 0px -50% 0px',
      threshold: [0, 0.15, 0.4, 0.75, 1]
    });

    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) io.observe(el);
    });
  })();

  /* ==========================================================================
     4. SMOOTH IN-PAGE ANCHORS
     ========================================================================== */

  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href*="#"]') : null;
    if (!a) return;
    if (a.hasAttribute('data-bh-jump-filter')) return; // handled below

    var href = a.getAttribute('href');
    if (!href || href === '#' || a.getAttribute('target') === '_blank') return;

    var id = href.slice(href.indexOf('#') + 1);
    if (!id) return;

    var target = document.getElementById(id);
    if (!target) return; // hash belongs to another page — let the browser handle it

    e.preventDefault();
    scrollToTarget(target);

    if (history.replaceState) history.replaceState(null, '', '#' + id);
  });

  /* Deep links (/#services) must land correctly on first paint.
     Lenis takes over scrolling as soon as it initialises, so re-apply the
     browser's native hash jump if images loading afterwards moved the target.

     NOTE: Lenis 1.1.11's `immediate: true` calls reset() after setScroll(),
     which snaps the position back to the stale value — so it is never used
     here. Misalignment is corrected with the normal animated scroll instead. */
  (function honourInitialHash() {
    if (!window.location.hash) return;

    var id = window.location.hash.slice(1);
    if (!id) return;

    var NAV_TOLERANCE = 130; // px; allow for the sticky navbar height

    var correct = function () {
      var target = document.getElementById(id);
      if (!target) return;

      // Already where we want to be? Leave the browser's jump alone.
      if (Math.abs(target.getBoundingClientRect().top - 100) < NAV_TOLERANCE) return;

      if (lenis) lenis.scrollTo(target, { offset: NAV_OFFSET });
      else window.scrollTo(0, target.getBoundingClientRect().top + window.pageYOffset - 100);
    };

    // Late-loading images change the document height, so re-check on load
    window.addEventListener('load', correct);
    window.setTimeout(correct, 1200);
  })();

  /* ==========================================================================
     5. MOBILE MENU
     ========================================================================== */

  (function mobileMenu() {
    var menu = document.querySelector('[data-bh-menu]');
    var burger = document.querySelector('[data-bh-burger]');
    if (!menu || !burger) return;

    var panel = menu.querySelector('[data-bh-menu-panel]');
    var backdrop = menu.querySelector('[data-bh-menu-backdrop]') || menu.querySelector('button');
    var scrollY = 0;
    var isOpen = false;

    function lockScroll(lock) {
      if (lock) {
        scrollY = window.pageYOffset;
        document.body.style.overflow = 'hidden';
        if (lenis) lenis.stop();
      } else {
        document.body.style.overflow = '';
        if (lenis) lenis.start();
      }
    }

    function open() {
      if (isOpen) return;
      isOpen = true;
      menu.hidden = false;
      burger.classList.add('is-open');
      burger.setAttribute('aria-expanded', 'true');

      // Force a reflow so the transition runs from the off-screen state
      void menu.offsetWidth;

      if (backdrop) backdrop.style.opacity = '1';
      if (panel) panel.style.transform = 'translateX(0)';

      lockScroll(true);
    }

    function close() {
      if (!isOpen) return;
      isOpen = false;
      burger.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');

      if (backdrop) backdrop.style.opacity = '0';
      if (panel) panel.style.transform = '';

      lockScroll(false);

      window.setTimeout(function () {
        if (!isOpen) menu.hidden = true;
      }, 500);
    }

    burger.addEventListener('click', function () {
      isOpen ? close() : open();
    });

    menu.addEventListener('click', function (e) {
      if (e.target.closest('[data-bh-menu-close]')) {
        close();
        return;
      }
      // Any navigation link inside the drawer closes it
      if (e.target.closest('[data-bh-menu-link]')) close();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) close();
    });

    // Close if the viewport grows past the drawer breakpoint
    window.addEventListener('resize', function () {
      if (isOpen && window.innerWidth >= 1024) close();
    });

    // If the page is loaded mid-way down, start in the scrolled state
    updateNav();
  })();

  /* ==========================================================================
     6. THEME TOGGLE (light / dark)
     ========================================================================== */

  (function themeToggle() {
    var buttons = document.querySelectorAll('[data-bh-theme-toggle]');
    if (!buttons.length) return;

    function current() {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    function apply(theme) {
      var isDark = theme === 'dark';
      document.documentElement.classList.toggle('dark', isDark);
      document.documentElement.style.colorScheme = theme;
      try {
        localStorage.setItem('bh-theme', theme);
      } catch (err) { /* private mode */ }

      buttons.forEach(function (b) {
        b.setAttribute('aria-pressed', String(isDark));
        b.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
      });
    }

    apply(current());

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        apply(current() === 'dark' ? 'light' : 'dark');
      });
    });

    // Follow the OS if the visitor has never chosen explicitly
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var onChange = function (e) {
      var stored = null;
      try { stored = localStorage.getItem('bh-theme'); } catch (err) { /* noop */ }
      if (!stored) apply(e.matches ? 'dark' : 'light');
    };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
    else if (mq.addListener) mq.addListener(onChange);
  })();

  /* ==========================================================================
     7. PORTFOLIO FILTERS + LOAD MORE
     ========================================================================== */

  (function portfolioFilters() {
    var grid = document.querySelector('[data-bh-grid]');
    var filterBtns = document.querySelectorAll('[data-bh-filter]');
    if (!grid || !filterBtns.length) return;

    var items = Array.prototype.slice.call(grid.querySelectorAll('[data-bh-item]'));
    var emptyState = grid.querySelector('[data-bh-empty]');
    var loadMoreBtn = document.querySelector('[data-bh-load-more]');
    var loadLabel = document.querySelector('[data-bh-load-label]');
    var countText = document.querySelector('[data-bh-item-count]');

    var PAGE_SIZE = 9;
    var active = 'all';
    var shown = PAGE_SIZE;

    function matches(item) {
      return active === 'all' || item.getAttribute('data-group') === active;
    }

    function apply() {
      var matching = items.filter(matches);
      var limit = Math.min(shown, matching.length);

      items.forEach(function (item) {
        var i = matching.indexOf(item);
        var visible = i > -1 && i < limit;
        item.hidden = !visible;
        if (visible) item.classList.add('is-in');
      });

      // Empty state
      if (emptyState) emptyState.hidden = matching.length !== 0;

      // Load more button
      if (loadMoreBtn) {
        var remaining = matching.length - limit;
        loadMoreBtn.hidden = remaining <= 0;
        if (loadLabel) {
          loadLabel.textContent = remaining > 0
            ? 'Load ' + remaining + ' more'
            : 'Load more projects';
        }
      }

      // Counter caption
      if (countText) {
        countText.textContent = matching.length
          ? 'Showing ' + limit + ' of ' + matching.length +
            (matching.length === 1 ? ' project' : ' projects')
          : '';
      }

      // Filter button state
      filterBtns.forEach(function (btn) {
        btn.setAttribute('aria-selected', String(btn.getAttribute('data-bh-filter') === active));
      });
    }

    function setFilter(value, opts) {
      opts = opts || {};
      active = value;
      shown = PAGE_SIZE;
      apply();
      if (opts.scroll !== false && opts.scroll) scrollToTarget(opts.scroll);
    }

    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setFilter(btn.getAttribute('data-bh-filter'));
      });
    });

    // Service cards can deep-link into a filter, e.g. "See software work"
    document.querySelectorAll('[data-bh-jump-filter]').forEach(function (link) {
      link.addEventListener('click', function () {
        setFilter(link.getAttribute('data-bh-jump-filter'));
        // the data-bh-scroll handler below performs the actual scroll
      });
    });

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', function () {
        shown += PAGE_SIZE;
        apply();
      });
    }

    apply();
  })();

  /* ==========================================================================
     7b. ALL-WORK PAGE FILTERS
     Same job as the homepage filter but with no paging — /portfolio/ is meant
     to show the whole archive at once, so there is no PAGE_SIZE and no load
     more button. It also keeps its own attribute names so the two scripts can
     never fight over the same grid if both ever appear on one page.
     ========================================================================== */

  (function workFilters() {
    var grid = document.querySelector('[data-bh-work-items]');
    var chipBar = document.querySelector('[data-bh-gallery-filters]');
    if (!grid || !chipBar) return;

    var chips = Array.prototype.slice.call(chipBar.querySelectorAll('[data-bh-gallery-filter]'));
    var items = Array.prototype.slice.call(grid.querySelectorAll('[data-bh-work-item]'));
    var empty = document.querySelector('[data-bh-work-empty]');
    var counter = document.querySelector('[data-bh-work-count]');
    var active = 'all';

    function apply() {
      var shown = 0;

      items.forEach(function (item) {
        var visible = active === 'all' || item.getAttribute('data-group') === active;
        item.hidden = !visible;
        if (visible) {
          shown++;
          item.classList.add('is-in');
        }
      });

      if (empty) empty.hidden = shown !== 0;
      if (counter) {
        counter.textContent = shown
          ? shown + (shown === 1 ? ' project' : ' projects')
          : '';
      }

      chips.forEach(function (chip) {
        chip.setAttribute(
          'aria-selected',
          String(chip.getAttribute('data-bh-gallery-filter') === active)
        );
      });
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        active = chip.getAttribute('data-bh-gallery-filter');
        apply();
      });
    });

    /* Deep link into a category, e.g. /portfolio/#software. Only the chips are
       consulted, so an unrelated hash is ignored. */
    var hash = (window.location.hash || '').replace('#', '');
    var isChip = chips.some(function (chip) {
      return chip.getAttribute('data-bh-gallery-filter') === hash;
    });
    if (isChip) active = hash;

    apply();
  })();

  /* ==========================================================================
     8. ANIMATED COUNTERS
     ========================================================================== */

  (function counters() {
    var nodes = document.querySelectorAll('[data-bh-count]');
    if (!nodes.length) return;

    function format(value, el) {
      var prefix = el.getAttribute('data-bh-prefix') || '';
      var suffix = el.getAttribute('data-bh-suffix') || '';
      return prefix + Math.round(value) + suffix;
    }

    function run(el) {
      var target = parseFloat(el.getAttribute('data-bh-count')) || 0;
      if (reducedMotion) {
        el.textContent = format(target, el);
        return;
      }

      var duration = 1500;
      var start = null;

      function step(time) {
        if (start === null) start = time;
        var progress = Math.min((time - start) / duration, 1);
        // easeOutExpo
        var eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        el.textContent = format(target * eased, el);
        if (progress < 1) window.requestAnimationFrame(step);
      }

      window.requestAnimationFrame(step);
    }

    if (!('IntersectionObserver' in window)) {
      nodes.forEach(run);
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          run(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    nodes.forEach(function (n) { io.observe(n); });
  })();

  /* ==========================================================================
     9. SCROLL REVEAL

     Deliberately scroll-driven rather than IntersectionObserver-based: an
     observer only samples at frame boundaries, so a fast Lenis scroll can
     carry an element past the viewport without it ever being reported
     "intersecting", which would leave it stuck at opacity 0 forever. This
     sweep is deterministic — anything whose top has passed the threshold is
     revealed, and the pending list shrinks to nothing over time.
     ========================================================================== */

  (function reveal() {
    var pending = Array.prototype.slice.call(document.querySelectorAll('.bh-reveal'));
    if (!pending.length) return;

    if (reducedMotion) {
      pending.forEach(function (n) { n.classList.add('is-in'); });
      return;
    }

    var ticking = false;

    function sweep() {
      ticking = false;
      if (!pending.length) return;

      var threshold = window.innerHeight * 0.94;
      var remaining = [];

      for (var i = 0; i < pending.length; i++) {
        if (pending[i].getBoundingClientRect().top < threshold) {
          pending[i].classList.add('is-in');
        } else {
          remaining.push(pending[i]);
        }
      }
      pending = remaining;
    }

    function schedule() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(sweep);
    }

    sweep();

    if (lenis) lenis.on('scroll', schedule);
    else window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
  })();

  /* ==========================================================================
     10. GO TO TOP
     ========================================================================== */

  (function goToTop() {
    var btn = document.getElementById('go_to_top_button');
    if (!btn) return;

    var ticking = false;

    function update() {
      ticking = false;
      var y = lenis ? lenis.scroll : window.pageYOffset;
      var show = y > 500;
      btn.classList.toggle('hidden', !show);
      btn.classList.toggle('flex', show);
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    if (lenis) lenis.on('scroll', onScroll);
    else window.addEventListener('scroll', onScroll, { passive: true });

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (lenis) {
        lenis.scrollTo(0, { duration: 1.2 });
      } else {
        window.scrollTo({ top: 0, behavior: reducedMotion ? 'auto' : 'smooth' });
      }
    });

    update();
  })();

  /* ==========================================================================
     11. FLASH MESSAGES
     ========================================================================== */

  (function flash() {
    var flash = document.getElementById('bh-flash');
    if (!flash) return;

    var dismissed = false;

    function hide() {
      if (dismissed) return;
      dismissed = true;
      flash.style.transition = 'opacity .4s ease, transform .4s ease';
      flash.style.opacity = '0';
      flash.style.transform = 'translate(-50%, -12px)';
      window.setTimeout(function () { flash.remove(); }, 420);
    }

    flash.querySelectorAll('[data-bh-dismiss]').forEach(function (btn) {
      btn.addEventListener('click', hide);
    });

    window.setTimeout(hide, 6000);
  })();

  /* ==========================================================================
     12. THIRD-PARTY GUARDS
        These libraries are also used by /blog and /admin, so only initialise
        them when their markup is actually on the page.
     ========================================================================== */

  if (typeof window.Swiper !== 'undefined') {
    var swiperConfigs = {
      '.mySwiper': {
        spaceBetween: 0,
        centeredSlides: true,
        loop: true,
        autoplay: { delay: 3500, disableOnInteraction: false },
        effect: 'fade',
        fadeEffect: { crossFade: true }
      },
      '.mySwiper2': {
        slidesPerView: 1,
        spaceBetween: 32,
        loop: true,
        autoplay: { delay: 3500, disableOnInteraction: false },
        navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
        breakpoints: {
          768: { slidesPerView: 2, spaceBetween: 32 },
          1024: { slidesPerView: 3, spaceBetween: 32 }
        }
      },
      '.mySwiper3': {
        slidesPerView: 2,
        spaceBetween: 10,
        loop: true,
        autoplay: { delay: 3000, disableOnInteraction: false },
        breakpoints: {
          768: { slidesPerView: 2, spaceBetween: 20 },
          1024: { slidesPerView: 3, spaceBetween: 40 },
          1536: { slidesPerView: 4, spaceBetween: 40 }
        }
      }
    };

    Object.keys(swiperConfigs).forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el) new window.Swiper(sel, swiperConfigs[sel]);
    });
  }

  if (typeof window.lightbox !== 'undefined') {
    window.lightbox.option({
      resizeDuration: 220,
      wrapAround: true,
      disableScrolling: true,
      /* Touch devices get no hover, so the arrows would stay invisible. */
      alwaysShowNavOnTouchDevices: true
    });

    /* `disableScrolling` only adds `lb-disable-scrolling` to <body>, which is
       useless here: the scroll container on this site is <html> (see input.css)
       and Lenis keeps calling scrollTo() on every frame, so the page drifted
       behind the overlay. Watch the class lightbox toggles and freeze both. */
    (function freezeScrollWhileLightboxOpen() {
      if (!('MutationObserver' in window)) return;

      var observer = new MutationObserver(function () {
        var locked = document.body.classList.contains('lb-disable-scrolling');
        document.documentElement.classList.toggle('bh-scroll-locked', locked);
        if (!lenis) return;
        if (locked) {
          lenis.stop();
        } else {
          lenis.start();
        }
      });

      observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    })();
  }
})();