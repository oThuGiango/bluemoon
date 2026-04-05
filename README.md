# 🏨 Dự án Quản lý Chung cư BlueMoon

Đây là một ứng dụng web (Web App) nội bộ, được xây dựng bằng Django, nhằm giúp Ban quản lý chung cư BlueMoon thực hiện các nghiệp vụ quản lý dân cư và thu phí dịch vụ.

## ⭐ Tính năng chính

### 1. Quản lý Hộ cư dân

- Xem danh sách toàn bộ hộ khẩu trong chung cư (`hrmanage`).
- Thêm một hộ khẩu mới (`add_hokhau`).
- Xem thông tin chi tiết của một hộ khẩu, bao gồm danh sách các thành viên thuộc hộ đó (`hokhau_detail`).
- Chỉnh sửa thông tin của hộ khẩu (số căn hộ, diện tích) (`edit_hokhau`).

### 2. Quản lý Nhân khẩu

- Xem danh sách toàn bộ nhân khẩu trong chung cư (`demomanage`).
- Thêm một nhân khẩu mới và liên kết họ vào một hộ khẩu (`add_demo`).
- Xem hồ sơ chi tiết của một nhân khẩu (`nhan_khau_profile`).
- Chỉnh sửa thông tin chi tiết của nhân khẩu (`edit_nhan_khau`).
- Xóa nhân khẩu ra khỏi hệ thống (`nhan_khau_delete`).

### 3. Quản lý Tài khoản

- Xem danh sách các tài khoản trong hệ thống (`accountmanage`).
- Thêm một tài khoản mới (username, password) và gán vai trò cho họ (`accountmanage_addaccount`).
- Xem thông tin chi tiết của một tài khoản (`view_taikhoan`).
- Chỉnh sửa thông tin tài khoản (cập nhật username, password, vai trò) (`edit_taikhoan`).

### 4. Chức năng chung

- Trang đăng nhập (`login`).
- Trang chủ (`home`).
- Trang hồ sơ cá nhân (`profile`).

---

## 🛠️ Công nghệ sử dụng

- **Backend:** **Python** (với framework **Django** ).
- **Frontend:** **HTML**, **CSS**, **JavaScript**.
- **Database:** **PostgreSQL** (Driver: `psycopg2-binary` ).

---

## 🚀 Hướng dẫn Cài đặt và Chạy

Đây là các bước để thiết lập và chạy dự án trên máy phát triển (local).

### 1. Yêu cầu

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/) (Bạn cần có một CSDL PostgreSQL đang chạy).

### 2. Các bước Cài đặt

1.  **Clone (tải) dự án về máy:**

    ```bash
    git clone [ĐƯỜNG DẪN GIT REPO CỦA BẠN]
    cd [TÊN THƯ MỤC DỰ ÁN]
    ```

2.  **Tạo và kích hoạt môi trường ảo (venv):**

    ```bash
    # Tạo venv
    py -m venv venv

    # Kích hoạt venv (trên Windows)
    .\venv\Scripts\activate
    ```

    _(Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh)._

3.  **Cài đặt các thư viện cần thiết:**
    _(Lệnh này sẽ đọc file `requirements.txt` và tự động cài Django & Psycopg2)_

    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình Database (Quan trọng):**
    Dự án này được thiết lập để kết nối với CSDL PostgreSQL.

    - Mở file `bluemoon_config/settings.py`.
    - Tìm đến phần `DATABASES`.
    - **Thay đổi** thông tin `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` để trỏ đến CSDL PostgreSQL **local** của bạn.

    _Ví dụ cấu hình CSDL local:_

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'bluemoon_db',  # Tên CSDL bạn đã tạo
            'USER': 'postgres',       # User của bạn
            'PASSWORD': 'password',   # Mật khẩu của bạn
            'HOST': 'localhost',      # Chạy ở local
            'PORT': '5432',           # Port mặc định của Postgres
        }
    }
    ```

5.  **Chạy "Migrations" (Tạo các bảng CSDL):**
    _(Lệnh này sẽ đọc `core/models.py` và tạo các bảng trong CSDL PostgreSQL bạn vừa cấu hình)_

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Tạo tài khoản Admin (Tổ trưởng) đầu tiên:**
    _(Chạy lệnh này và làm theo hướng dẫn để tạo tài khoản đăng nhập)_

    ```bash
    py manage.py createsuperuser
    ```

7.  **Chạy máy chủ (Server)!**
    ```bash
    py manage.py runserver
    ```

Bây giờ bạn có thể mở trình duyệt và truy cập vào `http://127.0.0.1:8000/` để xem ứng dụng web.

---

## 📁 Cấu trúc Thư mục

Dự án được tổ chức theo cấu trúc Django chuẩn:

```
BlueMoonProject/ (Thư mục gốc)
│
├── .env
├── db.sqlite3
├── manage.py             <-- File quản lý chính của Django
├── README.md
├── requirements.txt      <-- Danh sách thư viện 
├── structure.txt
│
├── core/                 <-- 📁 APP CHÍNH (chứa nghiệp vụ)
│   ├── models.py         
│   ├── views.py          
│   ├── tests.py
│   ├── urls.py
│   ├── admin.py
│   ├── forms.py
│   ├── apps.py
│   ├── __init__.py
│   ├── static/           <-- 📁 Chứa file "tĩnh" (CSS, JS, Images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/        <-- 📁 Chứa file HTML
│       └── core/
│           ├── accountmanage.html
│           ├── accountmanage_addaccount.html
│           ├── accountmanage_change.html
│           ├── accountmanage_view.html
│           ├── add_demo.html
│           ├── add_hokhau.html
│           ├── demomanage.html
│           ├── edit_nhan_khau.html
│           ├── header.html
│           ├── hokhau_detail.html
│           ├── hokhau_edit.html
│           ├── home.html
│           ├── hrmanage.html
│           ├── login.html
│           ├── main_page.html
│           ├── nhan_khau_delete.html
│           ├── nhan_khau_profile.html
│           ├── profile.html
│           ├── search.html
│           ├── Sidebar.html
│           ├── sidebar_and_footer.html
│           ├── temp.html
│           └── test.html
│
├── design/               <-- 📁 Thư mục thiết kế (Django không dùng)
│   └── Database/
│       ├── dbHandler.py
│       ├── khoi_tao_database.sql
│       ├── test.py
│       └── test_db.py
│
├── bluemoon_config/           <-- 📁 Thư mục Cấu hình Dự án
│   ├── settings.py       <-- File cài đặt chính 
│   ├── urls.py           <-- File URL tổng 
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
└── venv/                 <-- Thư mục môi trường ảo
```

---

## 👥 Tác giả
