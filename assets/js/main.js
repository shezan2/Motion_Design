const toggle = document.querySelector('.mobile-toggle');
const links = document.querySelector('.nav-links');
if (toggle && links) {
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}

const header = document.querySelector('.site-header');
const heroPanel = document.querySelector('.hero-panel');
if (header && heroPanel) {
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.3
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        header.classList.remove('visible');
      } else {
        header.classList.add('visible');
      }
    });
  }, observerOptions);
  observer.observe(heroPanel);
}
