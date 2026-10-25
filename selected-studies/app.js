'use strict';
const filters = [...document.querySelectorAll('[data-filter]')];
const studies = [...document.querySelectorAll('[data-category]')];
const result = document.querySelector('#result-count');
const categoryHashes = new Map([
  ['all', 'studies'],
  ['engineering', 'engineering'],
  ['design', 'editable-design'],
  ['motion', 'interaction-motion'],
  ['game-assets', 'game-assets']
]);
const hashCategories = new Map([...categoryHashes].map(([category, hash]) => [hash, category]));
const gameStudyIds = new Set(['tiled-map', 'character-walk']);

function showCategory(category) {
  const button = filters.find(item => item.dataset.filter === category);
  if (!button) return;
  filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  let visible = 0;
  studies.forEach(study => {
    const matches = category === 'game-assets'
      ? study.hasAttribute('data-game-asset')
      : study.dataset.category === category;
    study.hidden = category !== 'all' && !matches;
    if (!study.hidden) visible++;
  });
  const label = category === 'all' ? '' : ` · ${button.textContent.trim()}`;
  result.textContent = `${visible} ${visible === 1 ? 'study' : 'studies'}${label}`;
}

function syncFromHash() {
  let fragment;
  try {
    fragment = decodeURIComponent(window.location.hash.slice(1));
  } catch {
    return;
  }
  if (gameStudyIds.has(fragment)) {
    showCategory('game-assets');
    // Filtering changes the card's position; restore its actual fragment target.
    document.getElementById(fragment).scrollIntoView({ block: 'start' });
  } else if (!fragment) {
    showCategory('all');
  } else if (hashCategories.has(fragment)) {
    showCategory(hashCategories.get(fragment));
  }
  // Contact, top and unrelated fragments preserve the current selection.
}

filters.forEach(button => button.addEventListener('click', () => {
  const category = button.dataset.filter;
  showCategory(category);
  const hash = `#${categoryHashes.get(category)}`;
  if (window.location.hash !== hash) window.location.hash = hash;
}));
window.addEventListener('hashchange', syncFromHash);
syncFromHash();
