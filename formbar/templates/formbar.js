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

$('div.formbar-outline a').click(function() {
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
  $('.formbar-page').hide();
  $('#formbar-page-'+page).show();
});
/*
 * Evaluate when values in the form changes
*/
evaluateFields();
evaluateConditionals();
$('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').change(evaluateFields);
$('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').change(evaluateConditionals);

function evaluate(element) {
    var expr = element['attributes'][0].value;
    var tokens = expr.split(" ");

    var eval_expr = "";
    // Build evaluation string
    for (var j = tokens.length - 1; j >= 0; j--) {
        var tfield = null;
        var value = null;
        if (tokens[j].contains("$")) {
            tfield = tokens[j].replace('$', '');
            // Select field
            var field = $('input[name='+tfield+'], '
                          + 'select[name='+tfield+'], '
                          + 'textarea[name='+tfield+']');
            value = field.val();
            // If we can not get a value from an input fields the field my
            // be readonly. So get the value from the readonly element.
            if (!value) {
                value = $('div[name='+tfield+']').text();
            }
            console.log(tokens[j].replace('$', ''));
            eval_expr += value;
        } else {
            eval_expr += tokens[j];
        }
    }
    try {
        return eval(eval_expr);
    } catch (e) {
        console.log(e);
        return undefined;
    }
}

function evaluateConditionals() {
    var fieldsToEvaluate = $('.formbar-conditional');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--) {
        var conditional = fieldsToEvaluate[i];
        var readonly = $(conditional).attr('class').contains('readonly');
        var result = evaluate(conditional);
        if (result) {
            if (readonly) {
                $(conditional).animate({opacity:'1.0'}, 1500);
                $(conditional).find('input, select, textarea').attr('readonly', false);
            }
            else {
                $(conditional).show();
            }
        }
        else {
            if (readonly) {
                $(conditional).animate({opacity:'0.4'}, 1500);
                $(conditional).find('input, select, textarea').attr('readonly', true);
            }
            else {
                $(conditional).hide();
            }
        }
    }
}

function evaluateFields() {
    var fieldsToEvaluate = $('.formbar-evaluate');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--){
        var field = fieldsToEvaluate[i];
        var id = field['attributes'][1].value;
        var result = evaluate(field)
        if (result) {
            $('#'+id).text(result);
        }
        else {
            $('#'+id).text('NaN');
        }
    }
}
