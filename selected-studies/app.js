'use strict';
const filters = [...document.querySelectorAll('[data-filter]')];
const studies = [...document.querySelectorAll('[data-category]')];
const result = document.querySelector('#result-count');
filters.forEach(button => button.addEventListener('click', () => {
  const category = button.dataset.filter;
  filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  let visible = 0;
  studies.forEach(study => {
    study.hidden = category !== 'all' && study.dataset.category !== category;
    if (!study.hidden) visible++;
  });
  const label = category === 'all' ? '' : ` · ${button.textContent.trim()}`;
  result.textContent = `${visible} ${visible === 1 ? 'study' : 'studies'}${label}`;
}));
