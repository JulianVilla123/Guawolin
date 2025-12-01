document.addEventListener('DOMContentLoaded', function () {
  const profileBtn = document.getElementById('profileMenuBtn');
  const dropdown = document.getElementById('profileDropdown');

  if (profileBtn && dropdown) {
    profileBtn.addEventListener('click', function () {
      dropdown.classList.toggle('hidden');
    });

    // Opcional: cerrar el dropdown si haces clic fuera
    document.addEventListener('click', function (e) {
      if (!profileBtn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
  }
});
