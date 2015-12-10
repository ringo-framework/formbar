/* ATTENTION: This file is created with mako and includes some attribute which
 * are inserted dynamically */
var language = window.navigator.userLanguage || window.navigator.language;

$( document ).ready(function() {
    $('.formbar-tooltip').tooltip();
    $('.formbar-datepicker').datepicker({
        language: language,
        todayBtn: "linked",
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
      var baseurl = $(this).attr('formbar-baseurl');
      var timestamp = (new Date()).getTime()
      $.get(baseurl+'/set_current_form_page', 
            {
                page: page,
                item: item,
                itemid: itemid,
                timestamp: timestamp
            },
            function(data, status) {});
    });

    $('div.formbar-outline a').click(function() {
      var page = $(this).attr('href').split('#p')[1];
      var item = $(this).attr('formbar-item');
      var itemid = $(this).attr('formbar-itemid');
      var baseurl = $(this).attr('formbar-baseurl');
      $.get(baseurl+'/set_current_form_page', 
            {
                page: page,
                item: item,
                itemid: itemid
            },
            function(data, status) {});
      $('.formbar-page').hide();
      $('#formbar-page-'+page).show();
    });

    /* Restrict input depending on datatypes */
    $('div.formbar-form input.integer').keypress(function(key) {
        /* Only allow 0-9 (48-58) */
        var cc = key.charCode;
        if ((cc < 48 || cc > 57) && cc != 0){
            return false;
        }
    });
    $('div.formbar-form input.float').keypress(function(key) {
        /* Only allow 0-9 (48-58 and ".") */
        var cc = key.charCode;
        if ((cc < 48 || cc > 57) && cc != 0 && cc != 46){
            return false;
        }
    });
    $('div.formbar-form input.date').keypress(function(key) {
        /* Only allow 0-9 (48-58 and "-") */
        var cc = key.charCode;
        if ((cc < 48 || cc > 57) && cc != 0 && cc != 45){
            return false;
        }
    });
    $('div.formbar-form input.email').keypress(function(key) {
        /* Only allow a-z0-9-_@. (48-58 and "-") */
        var cc = key.charCode;
        console.log(cc)
        if ((cc < 97 || cc > 122) && (cc < 48 || cc > 57) && cc != 0 && cc != 45 && cc != 64 && cc != 95 && cc != 46){
            return false;
        }
    });


    /*
     * Evaluate when values in the form changes
    */
    evaluateFields();
    evaluateConditionals();
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').change(evaluateFields);
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').change(evaluateConditionals);
});

function evaluate(element) {
    var expr = element.getAttribute("expr");
    var tokens = expr.split(" ");

    var form = $(element).closest("form");
    var eval_url = $(form).attr("evalurl"); 

    var eval_expr = "";
    // Build evaluation string
    for (var j = 0; j <= tokens.length - 1; j++) {
        var tfield = null;
        var value = null;
        if (tokens[j].indexOf("$") >= 0) {
            tfield = tokens[j].replace('$', '');
            // Select field
            var field = $('input[name='+tfield+'], '
                          + 'select[name='+tfield+'], '
                          + 'div[name='+tfield+'], '
                          + 'textarea[name='+tfield+']');
            value = field.val();
            // If we can not get a value from an input fields the field my
            // be readonly. So get the value from the readonly element.
            // First try to get the unexpaned value, if there is no
            // value get the textvalue of the field. (Which is usually
            // the expanded value).
            if (!value) {
                value = field.attr("value");
            }
            if (!value) {
                value = field.text();
            }
            if (value.indexOf("[") < 0) {
                if (!value) {
                    value = "None";
                } else {
                    if (!$.isNumeric(value)) {
                        value = "'"+value+"'";
                    }
                }
            }
            eval_expr += " "+value;
        } else {
            eval_expr += " "+tokens[j];
        }
    }
    try {
        if (eval_url) {
            var result = false;
            $.ajax({
                type: "GET",
                async: false,
                url: eval_url,
                data: {rule: eval_expr},
                success: function (data) {
                    if (data.success) {
                        result = data.data;
                    } else {
                        result = data.data;
                    }
                },
                error: function (data) {
                    console.log("Request to eval server fails!");
                    result = false;
                }
            });
            return result;
        } else {
            return eval(eval_expr);
        }
    } catch (e) {
        console.log(e);
        return undefined;
    }
}

function evaluateConditionals() {
    var fieldsToEvaluate = $('.formbar-conditional');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--) {
        var conditional = fieldsToEvaluate[i];
        var readonly = $(conditional).attr('class').indexOf('readonly') >= 0;
        var result = evaluate(conditional);
        if (result) {
            if (readonly) {
                $(conditional).animate({opacity:'1.0'}, 1500);
                $(conditional).find('input, textarea').attr('readonly', false);
                $(conditional).find('select').attr('disabled', false);
            }
            else {
                $(conditional).show();
            }
        }
        else {
            if (readonly) {
                $(conditional).animate({opacity:'0.4'}, 1500);
                $(conditional).find('input, textarea').attr('readonly', true);
                $(conditional).find('select').attr('disabled', true);
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
