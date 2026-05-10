# 🏨 Dự án Quản lý Chung cư BlueMoon

Đây là một ứng dụng web (Web App) nội bộ, được xây dựng bằng Django, nhằm giúp Ban quản lý chung cư BlueMoon thực hiện các nghiệp vụ quản lý dân cư và thu phí dịch vụ.

## ⭐ Tính năng chính

### 1. Quản lý Hộ cư dân

- Xem danh sách toàn bộ hộ khẩu trong chung cư (`hrmanage`).
- Thêm một hộ khẩu mới (`add_hokhau`).
- Xem thông tin chi tiết của một hộ khẩu, bao gồm danh sách các thành viên thuộc hộ đó (`hokhau_detail`).
- Chỉnh sửa thông tin của hộ khẩu (`edit_hokhau`).

### 2. Quản lý Nhân khẩu

- Xem danh sách toàn bộ nhân khẩu trong chung cư (`demomanage`).
- Thêm một nhân khẩu mới và liên kết họ vào một hộ khẩu (`add_demo`).
- Xem hồ sơ chi tiết của một nhân khẩu (`nhan_khau_profile`).
- Chỉnh sửa thông tin chi tiết của nhân khẩu (`edit_nhan_khau`).
- Xóa nhân khẩu ra khỏi hệ thống (`nhan_khau_delete`).

### 3. Quản lý Tài khoản

- Xem danh sách các tài khoản trong hệ thống (`accountmanage`).
- Thêm một tài khoản mới (username, password) và gán vai trò cho họ (`add_account`).
- Xem thông tin chi tiết của một tài khoản (`view_account`).
- Chỉnh sửa thông tin tài khoản (cập nhật username, password, vai trò) (`edit_account`).

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

    ```bash
    copy env.example .env
    ```

    **Thay đổi** thông tin `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` để trỏ đến CSDL PostgreSQL của bạn.

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
├── core/**module                 <-- 📁 APP CHÍNH (chia theo từng nghiệp vụ)
│   ├── modules/               # Các module con: account, resident, fee, ...
│   ├── templates/             # Thư mục chứa các template HTML
│   ├── static/                # Thư mục chứa file tĩnh (CSS, JS, ảnh)
│   └── ...
│
├── bluemoon_config/           # Thư mục cấu hình dự án
│   ├── settings.py            # File cài đặt chính
│   ├── urls.py                # File URL tổng
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
└── venv/                      # Thư mục môi trường ảo (không commit lên git)
```

---

## 👥 Tác giả

Có sự tham gia của Github Copilot and ChatGPT ^^
