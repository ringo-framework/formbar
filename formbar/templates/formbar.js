$('.formbar-tooltip').tooltip();
$('.formbar-datepicker').datepicker({
    format: 'yyyy-mm-dd'
});
/*
* Set hidden form field "formbar-page" to the value of the currently
* selected page. This value will be used to set the currently selected
* page when the form ist rendered
*/
$('div.formbar-form form div.tabbable ul.nav li a').click(function() {
  var page = $(this).attr('href').split('#p')[1];
  var item = $(this).attr('formbar-item');
  var itemid = $(this).attr('formbar-itemid');
  $.get('/set_current_form_page', 
        {
            page: page,
            item: item,
            itemid: itemid
        },
        function(data, status) {});
});
