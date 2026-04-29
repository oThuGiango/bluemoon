document.addEventListener("DOMContentLoaded", function () {
  const tablePanel =
    document.querySelector(".main-content") ||
    document.querySelector(".history-panel");
  const modal = document.getElementById("mainModal");
  const modalContent = modal.querySelector(".modal-content");

  function openModal() {
    modal.classList.add("show");
    document.body.classList.add("modal-open");
  }

  function closeModal() {
    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
    modalContent.innerHTML = "";
  }

  // 2. Nút Hiện/Ẩn thêm hộ dân
  const btnToggle = document.querySelector("#btnToggleAddResident");

  if (btnToggle) {
    btnToggle.addEventListener("click", function () {
      const section = document.getElementById("addResidentSection");
      if (section) {
        const isHidden =
          section.style.display === "none" || section.style.display === "";
        section.style.display = isHidden ? "block" : "none";
        this.innerHTML = isHidden
          ? '<i class="fa-solid fa-xmark"></i> Hủy thêm hộ'
          : '<i class="fa-solid fa-user-plus"></i> Thêm hộ vào đợt này';
      }
    });
    attachModalListeners();
  }

  function attachModalListeners() {
    // 1. Đóng Modal
    modalContent
      .querySelectorAll(".modal-close-btn, #cancelDeleteBtn")
      .forEach((btn) => {
        btn.addEventListener("click", closeModal);
      });

    // 2. Logic tự động disable/enable ô Đơn giá khi chọn loại phí trong modal tạo khoản thu
    const phiBatBuocSelect = modalContent.querySelector(
      '[name="phi_bat_buoc"]',
    );
    const donGiaInput = modalContent.querySelector('[name="don_gia"]');
    const addFeeForm = modalContent.querySelector("#addFeeForm");
    const editFeeForm = modalContent.querySelector("#editFeeForm");

    function updateDonGiaField() {
      if (phiBatBuocSelect && donGiaInput) {
        if (phiBatBuocSelect.value === "False") {
          donGiaInput.value = 1;
          // donGiaInput.setAttribute("disabled", "disabled");
        } else {
          // donGiaInput.removeAttribute("disabled");
        }
      }
    }
    if (phiBatBuocSelect) {
      phiBatBuocSelect.addEventListener("change", updateDonGiaField);
      updateDonGiaField();
    }

    if (addFeeForm) {
      addFeeForm.addEventListener("submit", function () {
        if (donGiaInput) {
          donGiaInput.removeAttribute("disabled");
        }
      });
    }

    if (editFeeForm) {
      editFeeForm.addEventListener("submit", function () {
        if (donGiaInput) {
          donGiaInput.removeAttribute("disabled");
        }
      });
    }

    // 4. Nút Xác nhận thêm hộ (Gửi dữ liệu nhân lên Server)
    const btnAdd = document.querySelector("#btnConfirmAddResidents");
    if (btnAdd) {
      btnAdd.addEventListener("click", handleSaveNewResidents);
    }

    // 5. Nút Xác nhận đóng tiền (Thanh toán)
    const btnPay = document.querySelector("#btnConfirmPayment");
    if (btnPay) {
      btnPay.addEventListener("click", handleConfirmPayment);
    }

    // 6. Chọn tất cả hóa đơn trong bảng chờ thu
    const selectAll = document.querySelector("#selectAllInvoices");
    if (selectAll) {
      selectAll.addEventListener("change", function () {
        const checkboxes = document.querySelectorAll(
          'input[name="invoice_ids"]:not(:disabled)',
        );
        checkboxes.forEach((cb) => (cb.checked = this.checked));
      });
    }

    const confirmDeleteBtn = modalContent.querySelector("#confirmDeleteBtn");
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", function () {
        const form = modalContent.querySelector("form");
        if (!form) return;
        const url = form.action;
        const csrfToken = form.querySelector(
          "[name=csrfmiddlewaretoken]",
        ).value;
        fetch(url, {
          method: "POST",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken,
          },
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.status === "success") {
              alert(data.message);
              closeModal();
              window.location.reload();
            }
          })
          .catch((err) => alert("Lỗi khi xóa: " + err));
      });
    }

    // Khởi tạo Select2 cho tất cả các select có class 'select2' trong modal
    if (
      window.jQuery &&
      $(modalContent).find("select.select2").length > 0 &&
      $.fn.select2
    ) {
      $(modalContent)
        .find("select.select2")
        .select2({
          theme: "bootstrap-5",
          allowClear: true,
          placeholder: "Chọn các khoản thu...",
          dropdownParent: $(modalContent),
        });
    }
  }

  function handleSaveNewResidents() {
    const selectedRows = Array.from(
      document.querySelectorAll(".new-resident-row"),
    ).filter(
      (row) => row.querySelector('input[name="new_hokhau_ids"]').checked,
    );

    if (selectedRows.length === 0) {
      alert("Vui lòng chọn ít nhất một hộ dân!");
      return;
    }

    const dotThuId = document
      .querySelector("#display-dot-thu-id")
      .innerText.replace("#", "")
      .trim();

    const formData = new FormData();
    formData.append("id_dotthu", dotThuId);
    formData.append(
      "csrfmiddlewaretoken",
      document.querySelector("[name=csrfmiddlewaretoken]").value,
    );

    // Lấy info từ data attribute trên từng dòng đã chọn
    const hokhauDataList = [];
    selectedRows.forEach((row) => {
      const tongTien = row
        .querySelector(".new-tong-tien")
        .innerText.replace(/[^\d]/g, "");
      const chiTietTd = row.querySelector(".new-chi-tiet");
      const chiTietCount = parseInt(chiTietTd.dataset.chiTietCount || "0");
      const chiTietArr = [];
      for (let i = 1; i <= chiTietCount; i++) {
        chiTietArr.push({
          id_khoanthu: chiTietTd.getAttribute(`data-id-khoanthu-${i}`),
          so_luong: chiTietTd.getAttribute(`data-so-luong-${i}`),
          so_tien: chiTietTd.getAttribute(`data-so-tien-${i}`),
        });
      }
      const id_hokhau = row.querySelector('input[name="new_hokhau_ids"]').value;
      hokhauDataList.push({
        id_hokhau: id_hokhau,
        tong: tongTien,
        chi_tiet: chiTietArr,
      });
    });
    formData.append("hokhau_data", JSON.stringify(hokhauDataList));

    // Log toàn bộ formData để kiểm tra
    for (let pair of formData.entries()) {
      console.log(pair[0] + ":", pair[1]);
    }

    fetch("/create_invoices/", {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((res) => res.text())
      .then((html) => {
        alert("Đã thêm hộ và tạo hóa đơn thành công!");
        window.location.reload(); // F5 lại cả trang
      })
      .catch((err) => alert("Lỗi hệ thống: " + err));
  }

  function handleFormSubmission(e) {
    e.preventDefault(); // Chặn hành động chuyển trang của form

    const form = e.target;
    const formData = new FormData(form);
    const url = form.getAttribute("action") || window.location.href;

    fetch(url, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((res) => {
        if (res.ok) return res.json();
        return res.text().then((text) => {
          throw new Error(text);
        });
      })
      .then((data) => {
        if (data.status === "success") {
          alert("Tạo đợt thu thành công!");
          window.location.reload(); // ĐÂY LÀ DÒNG LÀM TƯƠI LẠI TRANG
        } else if (data.error) {
          alert(data.error);
        }
      })
      .catch((err) => {
        console.error(err);
        alert("Có lỗi xảy ra khi gửi dữ liệu.");
      });
  }

  // Xử lý xác nhận thanh toán (Cập nhật ngày nộp)
  function handleConfirmPayment() {
    const selectedIds = Array.from(
      document.querySelectorAll(
        'input[name="invoice_ids"]:checked:not(:disabled)',
      ),
    ).map((cb) => cb.value);
    if (selectedIds.length === 0) {
      alert("Vui lòng chọn ít nhất một hóa đơn cần thanh toán!");
      return;
    }

    if (confirm(`Xác nhận thanh toán cho ${selectedIds.length} hộ đã chọn?`)) {
      const formData = new FormData();
      selectedIds.forEach((id) => formData.append("invoice_ids[]", id));
      formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value,
      );

      fetch("/update_payment_status/", {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "success") {
            alert("Đã cập nhật ngày nộp tiền thành công!");
            // Tải lại trang chính để cập nhật số liệu tổng quan
            window.location.reload();
          } else {
            alert("Lỗi: " + data.message);
          }
        });
    }
  }

  // Hàm nạp Modal từ Server
  function loadAndOpenModal(url) {
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then((res) => res.text())
      .then((html) => {
        modalContent.innerHTML = html;
        openModal();
        attachModalListeners();
      });
  }

  // Lắng nghe sự kiện click vào các nút Xem chi tiết/Thêm mới trên bảng chính
  if (tablePanel) {
    tablePanel.addEventListener("click", (e) => {
      const trigger =
        e.target.closest(".modal-trigger") ||
        e.target.closest("#createNewFeeBtn");
      if (trigger) {
        e.preventDefault();
        loadAndOpenModal(trigger.getAttribute("data-url"));
      }
    });
  }
  document.addEventListener("click", (e) => {
    const deleteTrigger = e.target.closest(".btn-confirm-delete");
    if (deleteTrigger) {
      e.preventDefault();
      const url = deleteTrigger.getAttribute("data-url");
      // Nạp Modal xác nhận từ server (DeleteInvoiceModal.html / DeleteFeeModal.html)
      loadAndOpenModal(url);
    }
  });
  // Đóng khi click ra ngoài vùng Modal
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
});
