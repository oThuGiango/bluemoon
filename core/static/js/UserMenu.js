document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('userMenuBtn');
    const userMenu = document.getElementById('userMenu');
    const overlay = document.getElementById('userMenuOverlay');

    // Hàm xử lý Đóng/Mở
    function toggleMenu(){
        if(userMenu){
            userMenu.classList.toggle('show');
            if(overlay) overlay.classList.toggle('show');
        }
    }
    // Nhan nut mo menu
    if(menuBtn){
        menuBtn.addEventListener('click',function(e){
            e.stopPropagation();
            toggleMenu();
        });
    }

    //Hàm đóng menu
    function hideMenu(){
        if(userMenu){
            userMenu.classList.remove('show');
            if(overlay) overlay.classList.remove('show');
        }
    }

    // Sự kiện đóng menu khi bấm vào lớp phủ (overlay)
    if (overlay) {
        overlay.addEventListener('click', hideMenu);
    }
    //Đóng menu khi ấn Esc
    document.addEventListener('keydown',function(e){
        if(e.key === "Escape") hideMenu();
    });

    //Đóng menu khi click ra bất kỳ đâu ngoài vùng menu
    document.addEventListener('click', function(e) {
        if (userMenu && !userMenu.contains(e.target) && !menuBtn.contains(e.target)) {
            hideMenu();
        }
    });

    // Xử lý đăng xuất

    const logoutTrigger = document.getElementById('logout-trigger') || document.querySelector('[data-action="logout"]');
    const logoutForm = document.getElementById('logout-form');

    if(logoutTrigger && logoutForm){
        logoutTrigger.addEventListener('click',function(e){
            e.preventDefault();
            if (confirm("Bạn có chắc chắn muốn đăng xuất không?")) {
                logoutForm.submit(); // Gửi form POST 
            }
        });
    }
});


