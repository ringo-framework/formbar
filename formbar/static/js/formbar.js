/* ATTENTION: This file is created with mako and includes some attribute which
 * are inserted dynamically */
var language = null;
var fields2Conditionals = {};

function getBrowserLanguage() {
    var form = $('div.formbar-form form');
    var eval_url = $(form).attr("evalurl"); 
    if (!eval_url) {
        return window.navigator.userLanguage || window.navigator.language
    }
    var language = undefined;
    $.ajax({ 
        url: eval_url,
        async: false,
        data: {rule: "True"},
        success: function(data) {
                language = data.params.locale
            },
        error: function(data) {
                language = window.navigator.userLanguage || window.navigator.language
            }
    });
    return language;
}

$( document ).ready(function() {
    language = getBrowserLanguage();
    $('.formbar-tooltip').tooltip();
    $('.formbar-datepicker').datepicker({
        language: language,
        todayBtn: "linked",
        showOnFocus: false,
        autoclose: true
    });
    $('.list-group-item').on('click',function(e){
        var previous = $(this).closest(".list-group").children(".selected");
        previous.removeClass('selected'); // previous list-item
        $(e.target).addClass('selected'); // activated list-item
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
      $.get(baseurl+'/set_current_form_page', 
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
        /* Only allow 0-9 (48-58 and "-./") */
        var cc = key.charCode;
        if ((cc < 48 || cc > 57) && cc != 0 && (cc != 45 && cc != 46 && cc != 47)){
            return false;
        }
    });
    /*
     * Evaluate when values in the form changes
    */
    mapFieldsToConditionals();
    evaluateFields();
    evaluateConditionals();
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').not(":text").change(evaluateFields);
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').not(":text").change(function(event) {
        evaluateConditionalsOnChange(this);
        });

    //detection of user stoppy typing in input text fields
    var timer = null;
    $('div.formbar-form form input:text').keydown(function(){
        clearTimeout(timer);
        function evaluate(obj){
            evaluateFields();
            evaluateConditionalsOnChange(obj);
        }
        timer = setTimeout(evaluate, 750, this)
    });
});

function mapFieldsToConditionals() {
    var fieldsToEvaluate = $('.formbar-conditional');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--) {
        var conditional = fieldsToEvaluate[i];
        var tokens = conditional.getAttribute("expr").split(" ");
        for (var j = 0; j <= tokens.length - 1; j++) {
            var fieldname = null;
            var id = null;
            if (tokens[j].indexOf("$") >= 0) {
                fieldname = tokens[j].replace('$', '');
                if (fields2Conditionals[fieldname] == undefined ) {
                    fields2Conditionals[fieldname] = [];
                }
                id = conditional.getAttribute("id");
                if (fields2Conditionals[fieldname].indexOf(id) < 0) {
                    fields2Conditionals[fieldname].push(id);
                }
            }
        }
    }
}

function convertValue(value, field) {
    var cvalue = value;
    // Poor mans data conversion. In case that the datatype
    // (formbar datatype) is string, than out the value into single
    // quotes. Please note that the datatype attribute is currently only
    // renderered for the following fields:
    //  * radio
    if (field.attr("datatype") && field.attr("datatype") == "string") {
        cvalue = "'"+value+"'"
    }
    return cvalue;
}

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
            tfield = tokens[j].replace('$', '').replace('.', '\\.');
            // Select field
            var field = $('input[name='+tfield+'], '
                          + 'select[name='+tfield+'], '
                          + 'div[name='+tfield+'], '
                          + 'textarea[name='+tfield+']');
            // Get value from field depending on field type
            switch (field.attr("type")) {
                case 'radio':
                    value = convertValue($('input[name='+tfield+']:checked').val(), field);
                    break;
                case 'checkbox':
                    var allVals = [];
                    $('input[name='+tfield+']:checked').each(function() {
                        if ($(this).val() != "") {
                            allVals.push(convertValue($(this).val(), field));
                        }
                    });
                    value = '[' + allVals.join() + ']';
                    break;
                default:
                    value = convertValue(field.val(), field);
            }
            // If we can not get a value from an input fields the field my
            // be readonly. So get the value from the readonly element.
            // First try to get the unexpaned value, if there is no
            // value get the textvalue of the field. (Which is usually
            // the expanded value).
            if (!value && field.is("div")) {
                value = field.attr("value") || field.text()
                value = convertValue(value, field);
            }
            // If here is still no value we will set it to None. Otherwise the
            // the expression will not be valid E.g "== '2'"
            if (!value) {
                value = "None"
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
            return false;
        }
    } catch (e) {
        console.log(e);
        return undefined;
    }
}

function evaluateConditionals() {
    var fieldsToEvaluate = $('.formbar-conditional');
    for (var i = fieldsToEvaluate.length - 1; i >= 0; i--) {
        evaluateConditional(fieldsToEvaluate[i]);
    }
}

function evaluateConditional(conditional) {
    var readonly = $(conditional).attr('class').indexOf('readonly') >= 0;
    var result = evaluate(conditional);
    if (result) {
        if (readonly) {
            $(conditional).animate({opacity:'1.0'}, 500);
            $(conditional).find('input, textarea').attr('readonly', false);
            $(conditional).find('select').attr('disabled', false);
        }
        else {
            $(conditional).show();
        }
    }
    else {
        if (readonly) {
            $(conditional).animate({opacity:'0.4'}, 500);
            $(conditional).find('input, textarea').attr('readonly', true);
            $(conditional).find('select').attr('disabled', true);
        }
        else {
            $(conditional).hide();
        }
    }
}

// passing context as parameter until better solution is found
function evaluateConditionalsOnChange(obj) {
    var fieldname = obj.getAttribute("name")
    var conditionals = fields2Conditionals[fieldname];
    if (conditionals != undefined) {
        for (var j = 0; j <= conditionals.length - 1; j++) {
            evaluateConditional(document.getElementById(conditionals[j]));
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
