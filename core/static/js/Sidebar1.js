document.addEventListener('DOMContentLoaded', function() {
    

    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
        });
    }
});