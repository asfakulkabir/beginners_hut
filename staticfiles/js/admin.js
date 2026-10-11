/* Admin panel behaviour. No framework and no Flowbite — the panel is a data
   tool, so everything here is a few dozen lines of DOM wiring rather than a UI
   library. All hooks are `data-bh-*` so the markup stays readable.

   Loaded with a plain <script src> at the end of <body>, so the DOM is ready. */
(function () {
  'use strict';

  var root = document.documentElement;

  /* ---------------------------------------------------------------- drawer */
  var sidebar = document.getElementById('bh-sidebar');
  var backdrop = document.querySelector('[data-bh-drawer-close]');
  var drawerToggles = document.querySelectorAll('[data-bh-drawer-toggle]');

  function setDrawer(open) {
    if (!sidebar) return;
    sidebar.classList.toggle('is-open', open);
    if (backdrop) backdrop.classList.toggle('is-open', open);
    drawerToggles.forEach(function (btn) {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.body.classList.toggle('overflow-hidden', open);
  }

  drawerToggles.forEach(function (btn) {
    btn.addEventListener('click', function () {
      setDrawer(!sidebar.classList.contains('is-open'));
    });
  });

  if (backdrop) backdrop.addEventListener('click', function () { setDrawer(false); });

  /* ------------------------------------------------------------------ menu */
  var menuToggle = document.querySelector('[data-bh-menu-toggle]');
  var menu = document.querySelector('[data-bh-menu]');

  function setMenu(open) {
    if (!menu || !menuToggle) return;
    menu.classList.toggle('hidden', !open);
    menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      setMenu(menu.classList.contains('hidden'));
    });
  }

  document.addEventListener('click', function (event) {
    if (menu && !menu.classList.contains('hidden') && !menu.contains(event.target)) {
      setMenu(false);
    }
  });

  /* ----------------------------------------------------------------- theme */
  var themeToggle = document.querySelector('[data-bh-theme-toggle]');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var dark = root.classList.toggle('dark');
      localStorage.setItem('color-theme', dark ? 'dark' : 'light');
      /* Lets the dashboard chart re-read its colours. */
      window.dispatchEvent(new CustomEvent('bh:themechange', { detail: { dark: dark } }));
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (sidebar && sidebar.classList.contains('is-open')) setDrawer(false);
    setMenu(false);
  });

  /* ---------------------------------------------------------------- toasts */
  var TOAST_MS = 5000;

  function dismiss(toast) {
    if (!toast || toast.dataset.bhGone) return;
    toast.dataset.bhGone = '1';
    toast.style.transition = 'opacity .25s ease, transform .25s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-6px)';
    window.setTimeout(function () { toast.remove(); }, 260);
  }

  document.querySelectorAll('[data-bh-toast]').forEach(function (toast) {
    var close = toast.querySelector('[data-bh-toast-close]');
    if (close) close.addEventListener('click', function () { dismiss(toast); });
    window.setTimeout(function () { dismiss(toast); }, TOAST_MS);
  });

  /* ------------------------------------------------------- confirm dialog */
  /* One <dialog> for every destructive form on the page. The form is held back
     until the admin confirms, so nothing is posted by the accidental click. */
  var dialog = document.querySelector('[data-bh-dialog]');
  var pendingForm = null;

  function closeDialog() {
    if (dialog && dialog.open) dialog.close();
    pendingForm = null;
  }

  if (dialog) {
    var titleEl = dialog.querySelector('[data-bh-dialog-title]');
    var bodyEl = dialog.querySelector('[data-bh-dialog-body]');
    var confirmBtn = dialog.querySelector('[data-bh-dialog-confirm]');
    var cancelBtn = dialog.querySelector('[data-bh-dialog-cancel]');

    dialog.querySelectorAll('form[data-bh-confirm-title]').forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (form.dataset.bhConfirmed) return; // second pass: let it through
        event.preventDefault();
        pendingForm = form;
        titleEl.textContent = form.dataset.bhConfirmTitle || 'Are you sure?';
        bodyEl.textContent = form.dataset.bhConfirmBody || 'This cannot be undone.';
        confirmBtn.textContent = form.dataset.bhConfirmLabel || 'Delete';
        dialog.showModal();
      });
    });

    if (confirmBtn) {
      confirmBtn.addEventListener('click', function () {
        if (!pendingForm) return;
        pendingForm.dataset.bhConfirmed = '1';
        var form = pendingForm;
        closeDialog();
        form.submit();
      });
    }

    if (cancelBtn) cancelBtn.addEventListener('click', closeDialog);

    /* Esc and backdrop clicks both mean "no". */
    dialog.addEventListener('cancel', function (event) {
      event.preventDefault();
      closeDialog();
    });

    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) closeDialog();
    });
  }

  /* ------------------------------------------------- inbox expand / detail */
  document.querySelectorAll('[data-bh-expand]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var panel = document.getElementById(btn.getAttribute('aria-controls'));
      if (!panel) return;
      var open = panel.classList.toggle('hidden');
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    });
  });

  /* ------------------------------------------------------- dropzone + preview */
  document.querySelectorAll('[data-bh-dropzone]').forEach(function (zone) {
    var input = zone.querySelector('input[type="file"]');
    if (!input) return;

    ['dragenter', 'dragover'].forEach(function (type) {
      zone.addEventListener(type, function (event) {
        event.preventDefault();
        zone.classList.add('is-drag');
      });
    });

    ['dragleave', 'drop'].forEach(function (type) {
      zone.addEventListener(type, function () {
        zone.classList.remove('is-drag');
      });
    });

    zone.addEventListener('drop', function (event) {
      event.preventDefault();
      if (!event.dataTransfer || !event.dataTransfer.files.length) return;
      input.files = event.dataTransfer.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });

  function showPreview(input) {
    var form = input.closest('form');
    if (!form) return;
    var box = form.querySelector('[data-bh-preview]');
    var img = form.querySelector('[data-bh-preview-img]');
    var name = form.querySelector('[data-bh-preview-name]');
    if (!box || !img) return;

    var file = input.files && input.files[0];
    if (!file) {
      box.classList.remove('is-on');
      return;
    }

    if (name) name.textContent = file.name + ' · ' + Math.round(file.size / 1024) + ' KB';
    img.src = URL.createObjectURL(file);
    box.classList.add('is-on');
  }

  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () { showPreview(input); });
  });

  /* --------------------------------------------- CKEditor height + theming */
  if (window.CKEDITOR) {
    Object.keys(CKEDITOR.instances).forEach(function (name) {
      var editor = CKEDITOR.instances[name];
      if (!editor || !editor.container) return;
      editor.container.addClass('bh-editor-host');
      if (root.classList.contains('dark')) editor.container.addClass('bh-editor-dark');
    });
  }

  /* ---------------------------------------------------- search submits on enter */
  // The forms carry a real (screen-reader only) submit button, so the browser's
  // implicit submission is enough — no key handler needed here.
})();
