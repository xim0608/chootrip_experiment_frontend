(function ($) {
  $('.toggle-cart').on('click', function () {
    let $el = $(this);
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
        check_count()
      })
  });

  function check_count() {
    $.ajax({
      type: "GET",
      url: '/api/cart/count',
      dataType: "json",
    })
      .done(function (data) {
        $('#cart-count').text(data['count']);
      })
  };

})(jQuery);
