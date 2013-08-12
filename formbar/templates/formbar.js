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

/*
 * Evaluate when values in the form changes 
*/
$('div.formbar-form form input').change(function() {
    var fieldsToEvaluate = $('.formbar-evaluate');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--){
        var field = fieldsToEvaluate[i];
        var expr = field['attributes'][0].value;
        var id = field['attributes'][1].value;
        // Now get all $fieldnames
        var tokens = expr.split(" ");
        var eval_expr = "";
        for (var j = tokens.length - 1; j >= 0; j--){
            var tfield = null
            var value = null
            if (tokens[j].contains("$")) {
                tfield = tokens[j].replace('$', '');
                value = $('input[name='+tfield+']').val();
                console.log(tokens[j].replace('$', ''));
                eval_expr += value;
            } else {
                eval_expr += tokens[j];
            }
        };
        try {
            var eval_value = eval(eval_expr);
            $('#'+id).text(eval_value);
        } catch (e) {
            console.log(e);
            $('#'+id).text("");
        }
    };
});
