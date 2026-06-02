$(function () {
  function showMsg(html) {
    $("#assign-status-msg").html(html);
    setTimeout(() => $("#assign-status-msg").html(""), 3000);
  }

  function ajaxUpdate(url, data, csrfToken) {
    showMsg('<span style="color:#888">Đang cập nhật...</span>');
    $.ajax({
      url: url,
      type: "POST",
      dataType: "json",
      data: data,
      headers: {
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest",
      },
      success: function (res) {
        if (res.success) {
          showMsg('<span style="color:green">✓ Cập nhật thành công!</span>');
        } else {
          showMsg(
            '<span style="color:red">' +
              (res.error || "Có lỗi xảy ra!") +
              "</span>",
          );
        }
      },
      error: function (xhr) {
        const msg =
          xhr.responseJSON && xhr.responseJSON.error
            ? xhr.responseJSON.error
            : "Có lỗi xảy ra!";
        showMsg('<span style="color:red">' + msg + "</span>");
      },
    });
  }

  const $form = $("#ticket-assign-status-form");
  const csrf = $form.find('input[name="csrfmiddlewaretoken"]').val();
  const basePath = window.location.pathname; // e.g. /ticket/5/

  // Assignee onchange
  $("#assignee-select").on("change", function () {
    ajaxUpdate(basePath + "assign/", { assignee: $(this).val() }, csrf);
  });

  // Status onchange
  $("#status-select").on("change", function () {
    ajaxUpdate(basePath + "status/", { status: $(this).val() }, csrf);
  });

  // ── Response form (AJAX) ──
  $("#ticket-response-form").on("submit", function (e) {
    e.preventDefault();
    const content = $(this).find('textarea[name="content"]').val().trim();
    if (!content) return;
    const $btn = $(this).find('button[type="submit"]');
    $btn.prop("disabled", true);
    $.ajax({
      url: basePath + "response/",
      type: "POST",
      data: { content: content },
      headers: { "X-CSRFToken": csrf },
      success: function () {
        location.reload();
      },
      error: function (xhr) {
        const msg = xhr.responseJSON?.error || "Có lỗi xảy ra!";
        $("#response-msg").html('<span style="color:red">' + msg + "</span>");
        $btn.prop("disabled", false);
      },
    });
  });

  // ── Review form (AJAX) ──
  function paintStars(rating) {
    $(".td-star").each(function () {
      const starValue = Number($(this).data("value"));
      $(this).toggleClass("active", starValue <= rating);
    });
  }

  $(".td-star").on("click", function () {
    if ($("#ticket-review-form").data("reviewed") === 1) return;
    const rating = Number($(this).data("value"));
    $("#rating-value").val(rating);
    paintStars(rating);
  });

  $("#ticket-review-form").on("submit", function (e) {
    e.preventDefault();
    const rating = $("#rating-value").val();
    const review = $("#review-text").val().trim();
    if (!rating) return;
    const $btn = $(this).find('button[type="submit"]');
    $btn.prop("disabled", true);
    $.ajax({
      url: basePath + "review/",
      type: "POST",
      data: { rating: rating, review: review },
      headers: { "X-CSRFToken": csrf },
      success: function () {
        $("#review-msg").html(
          '<span style="color:green">✓ Đã gửi đánh giá!</span>',
        );
        $("#ticket-review-form").data("reviewed", 1);
        $(".td-star").prop("disabled", true);
        $("#review-text").prop("readonly", true);
        $("#review-submit-wrap").hide();
        $btn.prop("disabled", true);
      },
      error: function (xhr) {
        const msg = xhr.responseJSON?.error || "Có lỗi xảy ra!";
        $("#review-msg").html('<span style="color:red">' + msg + "</span>");
        $btn.prop("disabled", false);
      },
    });
  });
});
