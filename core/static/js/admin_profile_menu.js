document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("admProfileBtn");
  const pop = document.getElementById("admProfilePop");
  const overlay = document.getElementById("admPopOverlay");

  const logoutBtn = document.getElementById("admLogoutBtn");
  const logoutForm = document.getElementById("admLogoutForm");

  if (!btn || !pop || !overlay) return;

  const openMenu = () => {
    pop.classList.add("is-open");
    pop.setAttribute("aria-hidden", "false");
    btn.setAttribute("aria-expanded", "true");
    overlay.hidden = false;
  };

  const closeMenu = () => {
    pop.classList.remove("is-open");
    pop.setAttribute("aria-hidden", "true");
    btn.setAttribute("aria-expanded", "false");
    overlay.hidden = true;
  };

  const toggleMenu = () => {
    if (pop.classList.contains("is-open")) closeMenu();
    else openMenu();
  };

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  overlay.addEventListener("click", closeMenu);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });

  document.addEventListener("click", (e) => {
    // click ngoài pop và ngoài nút
    if (!pop.contains(e.target) && !btn.contains(e.target)) closeMenu();
  });

  // Logout POST + confirm
  if (logoutBtn && logoutForm) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      const ok = confirm("Bạn có chắc chắn muốn đăng xuất không?");
      if (ok) logoutForm.submit();
    });
  }
});
