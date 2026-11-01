/* One preference across catalogs and readers; no dependency on network/storage. */
(() => {
  const root = document.documentElement;
  const key = 'learning-notes-theme';
  const system = matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(key); } catch {}
  const valid = value => value === 'dark' || value === 'light';
  root.dataset.theme = valid(preference) ? preference : system.matches ? 'dark' : 'light';

  function updateControls() {
    const dark = root.dataset.theme === 'dark';
    for (const button of document.querySelectorAll('#theme, #theme-btn, .catalog-theme')) {
      button.setAttribute('aria-label', dark ? '切换浅色模式' : '切换深色模式');
      button.setAttribute('aria-pressed', String(dark));
      button.title = dark ? '切换浅色模式' : '切换深色模式';
      if (button.id !== 'theme-btn') button.textContent = dark ? '浅色' : '深色';
    }
  }
  new MutationObserver(() => {
    updateControls();
  }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  document.addEventListener('DOMContentLoaded', () => {
    updateControls();
    document.querySelector('.catalog-theme')?.addEventListener('click', () => {
      const value = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = value;
      preference = value;
      try { localStorage.setItem(key, value); } catch {}
    });
  });
  document.addEventListener('click', event => {
    if (event.target.closest('#theme, #theme-btn, .catalog-theme')) preference = root.dataset.theme;
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    preference = event.newValue;
    root.dataset.theme = valid(preference) ? preference : system.matches ? 'dark' : 'light';
  });
  system.addEventListener('change', event => {
    try { preference = localStorage.getItem(key); } catch {}
    if (!valid(preference)) root.dataset.theme = event.matches ? 'dark' : 'light';
  });
})();
