/* ATTENTION: This file is created with mako and includes some attribute which
 * are inserted dynamically */
var language = null;
var fields2Conditionals = {};
var currentFormValues = {}
var deactivator = function(event){ 
    $(this).prop("checked", !$(this).prop("checked"));
    event.preventDefault();
}

// Plugin to prevent double submission. See
// http://stackoverflow.com/questions/2830542/prevent-double-submission-of-forms-in-jquery
jQuery.fn.preventDoubleSubmission = function() {
  $(this).on('submit',function(e){
      var $form = $(this);
      if ($form.data('submitted') === true) {
        // Previously submitted - don't submit again
        e.preventDefault();
      } else {
        // Mark it so that the next submit can be
        // ignored
        $form.data('submitted', true);
      }
  });
// Keep chainability
return this;
};

/** This function will return the value of a given field. In case of radio,
 * select and checkbox fields it will return the value of the checked/selected
 * item/option of the field. */
function getFieldValue(field) {
    field= $(field);
    var ftype = field.attr("type");
    var fname = field.attr("name");
    if (ftype == "checkbox") {
        allVals = [];
        $("input[name='"+fname+"']:checked").each(function() {
            allVals.push($(this).val());
        });
        return allVals;
    } else if (ftype == "radio") {
        return $("input[name='"+fname+"']:checked").val()
    } else if (field.type == "select") {
        return $("input[name='"+fname+"']:selected").val()
    } else {
        return field.val();
    }
}

/** This function will set the value of a given field. In case of radio,
 * select and checkbox fields it will checke/select ithe item/option of the
 * field. */
function setFieldValue(field, value, remember) {
    if ( remember == undefined ) {
        remember = true;
    }
    field= $(field);
    var ftype = field.attr("type");
    var fname = field.attr("name");
    if (value && remember && !field.attr("readOnly")) {
        currentFormValues[fname] = getFieldValue(field);
    }

    if (ftype == "radio") {
        if (field.val() == value) {
            field.prop("checked", true);
        } else {
            field.prop("checked", false);
        }
    } else if (ftype == "checkbox") {
        if (currentFormValues[fname].indexOf(field.val()) > -1) {
            field.prop("checked", true);
        } else {
            field.prop("checked", false);
        }
    } else if (field.type == "select") {
        if (field.val() == value) {
            field.prop("selected", true);
        } else {
            field.prop("selected", false);
        }
    } else {
        field.val(value);
    }

}

/** Will remove the value of all fields within the given conditional to an empyt
 * string which is the default value in most cases. */
function removeValues(conditional) {
    var inputs = $(conditional).find(":input");
    for (var i = 0, len = inputs.length; i < len; i++) {
        var field = $(inputs[i]);
        setFieldValue(field, "");
    }
}

/** Will reset the value of all fields within a given conditional to the
 * initial value saved in the given value object. */
function resetValues(conditional, values) {
    var inputs = $(conditional).find(":input");
    for (var i = 0, len = inputs.length; i < len; i++) {
        var field = inputs[i];
        setFieldValue(field, values[$(field).attr('name')], false);
    }
}


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

    // If the form has pages and there are no input elements on the current
    // form page, than hide the submit button.
    selected_formpage = $('.formbar-page :visible');
    if (selected_formpage.length > 0) {
        toggleSubmit(selected_formpage);
    }

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
      var timestamp = (new Date()).getTime()
      $.get(baseurl+'/set_current_form_page', 
            {
                page: page,
                item: item,
                itemid: itemid,
                timestamp: timestamp
            },
            function(data, status) {});
      $('.formbar-page').hide();
      $('#formbar-page-'+page).show();
      // If there are no input elements on the current form page, than hide
      // the submit button.
      var formpage = $('#formbar-page-'+page);
      toggleSubmit(formpage);
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
    setInitialFormValues();
    mapFieldsToConditionals();
    evaluateFields();
    evaluateConditionals();
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').not(":text").change(evaluateFields);
    $('div.formbar-form form input, div.formbar-form form select,  div.formbar-form form textarea').not(":text").change(function(event) {
        setFieldValue(this, $(this).val());
        evaluateConditionalsOnChange(this);
        });

    //detection of user stoppy typing in input text fields
    var timer = null;
    $('div.formbar-form form input:text').keydown(function(){
        clearTimeout(timer);
        function evaluate(obj){
            setFieldValue(obj, $(obj).val());
            evaluateFields();
            evaluateConditionalsOnChange(obj);
        }
        timer = setTimeout(evaluate, 750, this)
    });
    $('div.formbar-form form').not(".disable-double-submit-prevention").preventDoubleSubmission();

});


/** Will save the initial values of all fields in the form in a global
 * variable called `currentFormValues`. The varibable is used to reset the value
 * of the field to its initial value in case a value has been removed after it
 * becomes readonly/invisible in a conditional and now gets activated again. */
function setInitialFormValues() {
    var fields = $('div.formbar-form :input');
    for (var i = 0, len = fields.length; i < len; i++) {
        if (currentFormValues[fields[i].name] == undefined) {
            currentFormValues[fields[i].name] = getFieldValue(fields[i]);
        }
    }
}

/* Map fields to conditionals. That means map every conditional to the field
 * where the expression of the condition refers to the field. Later if a value
 * of a field changes we know which conditionals need to be reevaluated. */
function mapFieldsToConditionals() {
    var conditionals = $('.formbar-conditional');
    // FIXME: Iteration order counts to make cascading conditionals and
    // resetting work! Currently we are assuming, that rules which occour
    // later in the document may be preconditionedby former rules. So when
    // resetting conditionals in the form it is important to handle
    // conditionals in the correct order to allow cascading resets.
    for (var i = 0; i <= conditionals.length - 1; i++) {
        var conditional = conditionals[i];
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
    if ((field.attr("datatype") && field.attr("datatype") == "string")) {
        cvalue = "'"+value+"'"
    }
    if ((field.attr("datatype") && field.attr("datatype") == "date")) {
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
    var reset = $(conditional).attr('reset-value').indexOf('true') >= 0;
    var readonly = $(conditional).attr('class').indexOf('readonly') >= 0;
    var result = evaluate(conditional);
    if (result) {
        $(conditional).find(':radio, :checkbox').unbind('click',deactivator);
        if (readonly) {
            $(conditional).animate({opacity:'1.0'}, 500);
            $(conditional).find('input, textarea').attr('readonly', false);
            $(conditional).find('select').attr('disabled', false);
        }
        else {
            $(conditional).show();
        }
        if (reset) {
            resetValues(conditional, currentFormValues);
        }
    }
    else {
        $(conditional).find(':radio, :checkbox').click(deactivator);
        if (readonly) {
            $(conditional).animate({opacity:'0.4'}, 500);
            $(conditional).find('input, textarea').attr('readonly', true);
            $(conditional).find('select').attr('disabled', true);
        }
        else {
            $(conditional).hide();
        }
        if (reset) {
            removeValues(conditional);
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

function toggleSubmit(element) {
  var button = $('.formbar-form :submit');
  if ( element.find("input[type!='hidden'], select, textarea").filter(":visible").length > 0) {
      button.show();
  } else {
      button.hide();
  }
}
