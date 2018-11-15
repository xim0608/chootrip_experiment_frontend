(function ($) {
  function changeCount() {
    $.ajax({
      type: "GET",
      url: '/api/cart/count',
      dataType: "json",
    })
      .done(function (data) {
        $('#cart-count').text(data['count']);
      })
  };


  $('.toggle-cart').on('click', function () {
    let $el = $(this);

    let under10 = true;

    $.when(
      $.ajax({
        type: "GET",
        url: '/api/cart/count',
        dataType: "json",
      })
        .done(function (data) {
          if (data['count'] === 10) {
            if ($el.text() === "追加する") {
              alert('すでに10件登録されています');
              under10 = false;
            }
          }
        })
    ).done(function () {
      if (under10) {
        let url = '/api/cart/add/' + $el.data('id');
        $.ajax({
          type: "GET",
          url: url,
          dataType: "json",
        })
          .done(function (data) {
            if (data['status'] === 'added') {
              $el.text('追加済み');
              $el.addClass('btn-primary');
              $el.removeClass('btn-outline-primary');
              alert('追加されました');
            } else {
              $el.text('追加する');
              $el.addClass('btn-outline-primary');
              $el.removeClass('btn-primary');
              alert('削除しました');
            }
            changeCount()
          })
      }
    })
  });


})(jQuery);
