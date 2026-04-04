// Element references
const btnOpen = document.getElementById('btnOpen');
const btnClose = document.getElementById('btnClose');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const mainContent = document.getElementById('mainContent');

function openSidebar() {
  sidebar.classList.add('open');
  overlay.classList.add('visible');
  btnOpen.setAttribute('aria-expanded', 'true');
  sidebar.setAttribute('aria-hidden', 'false');
  overlay.hidden = false;
  // optional: push content on wide screens
  if (window.innerWidth >= 900) mainContent.classList.add('shift');

  // put focus on first focusable item inside sidebar for accessibility
  const focusable = sidebar.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (focusable.length) focusable[0].focus();
}

function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.classList.remove('visible');
  btnOpen.setAttribute('aria-expanded', 'false');
  sidebar.setAttribute('aria-hidden', 'true');
  overlay.hidden = true;
  mainContent.classList.remove('shift');
  btnOpen.focus();
}

btnOpen.addEventListener('click', openSidebar);
btnClose.addEventListener('click', closeSidebar);
overlay.addEventListener('click', closeSidebar);

// close with Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && sidebar.classList.contains('open')) {
    closeSidebar();
  }
});
