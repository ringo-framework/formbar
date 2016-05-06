/* Formbar rewrite */

/** 
 * @function
 * reduce is defined as a shortcut to [].reduce()
 */
var reduce = Function.prototype.call.bind([].reduce)
var map = Function.prototype.call.bind([].map)

/** 
 * @module
 * Conatins the mechanics for evaluating fields and communication results
 * from the server back to the application. Is used by the form-component
 *  
 * @public
 * @function
 * 
 * init - initialization of the engine
 * changeField - eventhandler 
 * communicates field-changes to the server and evaluates rules
 */
var ruleEngine = function () {
  var targetFields;
  var conditionals;

  /** 
   * @function
   * 
   * scans the form for conditionals
   * takes expressions like "bool( $qeoi.lm_employment_category_unemployed )" 
   * from the div-Attribute and extracts the Variables  
   * ("$qeoi.lm_employment_category_unemployed") and stores for every variable
   * in which div it occurs and its according expression
   * 
   */
  var scanConditionals = function () {
    return reduce($('.formbar-conditional'), function (o, n) {
      var expr = n.getAttribute("expr");
      var tokens = expr.split(" ");
      var id = n.getAttribute("id");
      tokens.forEach(function (token) {
        if (token[0] === '$') {
          var fieldName = token.replace("$", '');
          if (!o[fieldName]) o[fieldName] = {};
          o[fieldName][id] = {
            "id": id,
            "expr": expr
          };
        }
      });
      return o;
    }, {});
  };

  /** 
   * @function
   * 
   * delegates the evaluation for the field to the server
   * 
   * @param {string} expression - holding the expression without variables
   * 
   * @param {string} divId - holding the ID of the div for further processing in 
   * the callback
   * 
   * @param {function} callback - the function which is called with the result
   */
  var checkFields = function (expression, divId, callBack) {
    var form = $("#" + divId).closest("form");
    var eval_url = $(form).attr("evalurl");
    var ruleParam = "?rule=" + encodeURIComponent(expression);
    $.ajax({
      type: "GET",
      url: eval_url + ruleParam,
      success: function (data) {
        callBack(data.data, divId);
      },
      error: function (data) {
        console.log("Request to eval server fails!")
      }
    });
  };

  /**
   * @function
   * 
   * takes expressions, looks up the values of the variables and substitutes
   * them in the expression
   * 
   * @param {string} expression the expression to be evaluated
   * 
   * @param {Object} map for lookup of variables
   * 
   */
  var substituteExpression = function (expression, currentValues) {
    return expression.split(" ").map(function (token) {
      if (token[0] === '$') {
        currentValue = currentValues[token.replace("$", "")].value || "None";
        token = currentValue;
        if (Array.isArray(currentValue)) {
          token = "[" + currentValue.join(",") + "]";
        }
      }
      return token;
    }).join("  ");
  }

  /**
   * @function 
   * 
   * changeField is exported.
   * It is used as a callable for field-change-events
   * 
   * @param {string} name - the name of the field / variable which is changed
   * 
   * @param {Object} currentValues - holds the current state of all fields
   * 
   * @param {function} callBack - a function to call back after evaluation
   * 
   */
  var changeField = function (name, currentValues, callBack) {
    if (conditionals[name]) {
      var rules = conditionals[name];
      Object.keys(rules).forEach(function (k) {
        checkFields(substituteExpression(rules[k].expr, currentValues), k, callBack);
      });
    }
    return true;
  }

  var init = function () {
    conditionals = scanConditionals();
  };
  return {
    init: init,
    changeField: changeField
  };
} ();

/**
 * @module
 * 
 * is responsible for evaluating inputevents
 * 
 * @public
 * @function
 * 
 * integer - evaluates integer keys
 *
 * @public
 * @function
 * 
 * float - evaluates integer keys
 *
 * @public
 * @function
 * 
 * date - evaluates integer keys 
 */
var inputFilter = function () {
  var zero = "0".charCodeAt(0);
  var nine = "9".charCodeAt(0);
  var point = ".".charCodeAt(0);
  var minus = "-".charCodeAt(0);
  var slash = "/".charCodeAt(0);

  /**
   * @function
   * 
   * @param {string} key
   * 
   * results in true only for 0 - 9
   * 
   */
  var integer = function (key) {
    return !(key.charCode !== 0 && (key.charCode < zero || key.charCode > nine));
  };


  /**
   * @function
   * 
   * @param {string} key 
   * 
   * results in true only for 0 - 9 and .
   *
   */
  var float = function (key) {
    return !(key.charCode !== 0 && key.charCode !== point && (key.charCode < zero || key.charCode > nine));
  };

  /**
   * @function
   * 
   * @param {string} key 
   * 
   * results in true only for 0 - 9, . and /
   *
   */
  var date = function (key) {
    return !(key.charCode !== 0 && key.charCode !== point && key.charCode !== slash && (key.charCode < zero || key.charCode > nine));
  };

  return {
    integer: integer,
    float: float,
    date: date
  };
} ();

/**
 * 
 * @module
 * 
 * @requires inputFilter, ruleEngine
 * 
 * The form module is responsible for handling form events for setting
 * and ressetting of values, evaluating the rules and promote changes to
 * the appropriate fields
 * 
 * @public
 * @function
 * 
 * init - inits the form 
 * 
 */
var form = function (inputFilter, ruleEngine) {
  var formFields = {};

  /**
   * @function
   * 
   * @param {Object} f - the field in form of a DOM-element
   *
   * extracts the value from DOM-elements
   * 
   */
  var getFieldValue = function (f) {
    var field = $(f);
    var ftype = field.attr("type");
    var fname = field.attr("name");
    var result;
    switch (ftype) {
      case "checkbox":
        result = [];
        $("input[name='" + fname + "']:checked:visible").each(function () {
          result.push($(this).val());
        });
        break;
      case "radio":
        result = $("input[name='" + fname + "']:checked:visible").val();
        break;
      default:
        result = field.val();
        break;
    }
    return result;
  };

  /**
   * @function
   * 
   * @param {string} fieldname - the name of the field to clear
   *
   * unsets the value of a field with a given name
   * 
   */
  var clearFieldValue = function (fieldName) {
    var field = $("[name='" + fieldName + "']")[0];
    if (field.tagName === 'INPUT') {
      var ftype = field.getAttribute("type");
      switch (ftype) {
        case "checkbox":
          $("[name='"+fieldName+"']:visible:checked").each(function(i,x){$(x).prop("checked", false);})
          break;
        case "radio":
          $("input[name='" + fieldName + "'][value='']").prop("checked", true);
          break;
        default:
          $("input[name='" + fieldName + "']").val("");
          break;
      }
    } else if (field.tagName === 'SELECT') {
      $("select[name='" + fieldName + "']").val("");
    }
  }

  /**
   * @function
   * 
   * @param {string} fieldName - the name of the field to re-set the value
   * 
   * @param {Object} formFields - the current state
   *
   * restores the value of field to the value before clearFieldValue was called
   * 
   * this is the inverse operation to clearFieldValue
   * 
   */
  var resetFieldValue = function (fieldName, formFields) {
    var field = $("[name='" + fieldName + "']")[0];
    if (field.tagName === 'INPUT') {
      var ftype = field.getAttribute("type");
      switch (ftype) {
        case "checkbox":
          formFields[fieldName].value.forEach(function(x){ $("[name='qeri.job_position'][value='"+x+"']").prop("checked", true); });
          break;
        case "radio":
          $("input[name='" + fieldName + "'][value='" + formFields[fieldName].value + "']").prop("checked", true);
          break;
        default:
          $(field).val(formFields[fieldName].value);
          break;
      }
    } else if (field.tagName === 'SELECT') {
      $("select[name='" + fieldName + "']").val(formFields[fieldName].value);
    }
  }

  /**
   * @function
   * 
   * sets the eventlisteners for the input fields
   * 
   */
  var initInputFilters = function () {
    $('div.formbar-form input.integer').keypress(inputFilter.integer);
    $('div.formbar-form input.float').keypress(inputFilter.float);
    $('div.formbar-form input.date').keypress(inputFilter.date);
  };


  /**
   * @function
   * 
   * scans every form-group and gathers every INPUT.
   * holds state ("active/inactive", value, required, desired) information of
   * these elements. Acts as a simple model.
   *
   */
  var scanComponents = function () {
    var groups = $(".form-group");
    groups.map(function (i, x) {
      var name = $(x).attr("formgroup");
      if (name) {
        var state = ($(x).hasClass("active")) ? "active" : "inactive";
        var value = getFieldValue($(x).find("input")[0]);
        var desired = $(x).attr("desired");
        var required = x.getAttribute("required");
        formFields[name] = {
          'state': state,
          'value': value,
          'desired': desired,
          'required': required
        };
      }
    });
  };

  /**
   * @function
   * 
   * is called after evaluation of rules.
   * handles fadeIn/Out and actualization of fields
   *
   * @param {Object} result - of evaluation from server
   *
   * @param {string} divId - the Id of the div 
   *
   * @param {string} elementName - name of the element for which the rule was evaluated
   * a lookup in formFields gets you the state of the field
   * 
   */
  var toggleConditional = function (result, divId) {
    var element = $("#" + divId);
    if ($(element).hasClass("readonly")) handleReadOnly(result, element);
  }

  var handleReadOnly = function (result, div) {
    fieldsToUpdate = map(div.find(".form-group"), (function (x) {
      return x.getAttribute("formgroup");
    }));

    fieldsToUpdate.forEach(function (fieldName) {
      var field = formFields[fieldName];
      var oldState = field.state;
      var newState = oldState;
      if (result == true && oldState == "inactive") {
        resetFieldValue(fieldName, formFields);
        newState = "active";
        if (field.value === "") activateDesired(fieldName);
      }
      if (result == false && oldState == "active") {
        clearFieldValue(fieldName);
        newState = "inactive";
        deactivateDesired(fieldName);
      }
      if (!(oldState == newState)) {
        field.state = newState;
        $(".form-group[formgroup='" + fieldName + "']").removeClass(oldState).addClass(newState);
        $(".form-group[formgroup='" + fieldName + "']").find(':input:disabled').prop('disabled', true);
        triggerChange(fieldName);
      }
    });
  }

  var deactivateDesired = function (fieldName) {
    var field = formFields[fieldName];
    if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
      $(".form-group[formgroup='" + fieldName + "']").removeClass("has-warning");
      $(".form-group[formgroup='" + fieldName + "']").find(".help-block[desired='True']").addClass("hidden");
    }
  }
  var activateDesired = function (fieldName) {
    var field = formFields[fieldName];
    if (field.desired === "True" && !$(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
      $(".form-group[formgroup='" + fieldName + "']").addClass("has-warning");
      $(".form-group[formgroup='" + fieldName + "']").find(".help-block[desired='True']").removeClass("hidden");
    }
  }

  /**
   * @function
   *
   * triggers changes via ruleEngine
   *
   * @param {string} field name - the name of the field, which is changed
   *
   */
  var triggerChange = function (fieldName) {
    ruleEngine.changeField(fieldName, formFields, function (data, divId) {
      toggleConditional(data, divId);
    });
  };
  /**
   * @function
   * 
   * is called when any INPUT changes
   *
   * @param {Object} the event object fired by the DOM
   * 
   */
  var inputChanged = function (e) {
    var target = e.target;
    var value = getFieldValue(target);
    formFields[target.name].value = value;
    setDesiredStateForCurrentField(target.name);
    triggerChange(target.name);
  };


  var setDesiredStateForCurrentField = function (fieldName) {
    var element = formFields[fieldName];
    if (element.value === "" && element.desired === "True") activateDesired(fieldName);
    if (element.value !== "" && element.desired === "True") deactivateDesired(fieldName);
  }

  /**
   * @function
   * 
   * sets the global listener for changes in INPUT / SELECT 
   *
   */
  var setListener = function () {
    $("body").on("change", function (e) {
      switch (e.target.tagName) {
        case 'INPUT':
        case 'SELECT':
          inputChanged(e);
          break;
        default:
          break;
      }
    });
  };

  var init = function () {
    initInputFilters();
    scanComponents();
    setListener();
    ruleEngine.init();
  };
  return {
    init: init
  };
} (inputFilter, ruleEngine);


/**
 * @module 
 * formbar
 * 
 * @depends on for
 * 
 * wires up the formhandling process
 * initializes datepickes
 * sets up navigation
 * 
 * @public
 * @function
 * 
 * init - initializes formbar
 * 
 */
var formbar = function (form) {
  var getBrowserLanguage = function getBrowserLanguage() {
    var lang = "en";
    if (navigator.browserLanguage) {
      lang = navigator.browserLanguage;
    } else if (navigator.languages) {
      lang = navigator.languages[0];
    } else {
      lang = navigator.language;
    }
    return lang;
  };

  /**
   * @function 
   * handles listgroup-items
   * 
   * @param {Object} - the event-Object
   *
   */
  var selectListGroupItem = function (e) {
    var previous = $(this).closest(".list-group").children(".selected").removeClass('selected');
    $(e.target).addClass('selected');
  };

  /**
   * @function 
   * hides submit button in case of an empty input page
   * 
   * @param {Object} - the DOM-Element
   *
   */
  var hideSubmitButtonOnInputlessPage = function (element) {
    var button = $('.formbar-form :submit');
    if (element.find("input[type!='hidden'], select, textarea").filter(":visible").length > 0) {
      button.show();
    } else {
      button.hide();
    }
  };

  /**
   * @function
   * 
   * handles hiding of submitbutton
   *
   */
  var initSubmit = function () {
    var selected_formpage = $('.formbar-page :visible');
    if (selected_formpage.length > 0) {
      hideSubmitButtonOnInputlessPage(selected_formpage);
    }
  };

  /**
   * @function
   * 
   * handles initialization of date-Picker
   *
   */
  var initDatePicker = function () {
    var browserLanguage = getBrowserLanguage();
    $('.formbar-datepicker').datepicker({
      language: browserLanguage,
      todayBtn: "linked",
      showOnFocus: false,
      autoclose: true
    });
  };

  /**
   * @function
   * 
   * sets selected page
   *
   */
  var setSelectedPage = function (e) {
    var target = e.target;
    var page = $(target).attr('href').split('#p')[1];
    var item = $(target).attr('formbar-item');
    var itemid = $(target).attr('formbar-itemid');
    var baseurl = $(target).attr('formbar-baseurl');
    var timestamp = (new Date()).getTime()
    $.get(baseurl + '/set_current_form_page', {
      page: page,
      item: item,
      itemid: itemid,
      timestamp: timestamp
    });
  };

  /**
   * @function
   * 
   * handles navigation for the sidetabs
   *
   */
  var navigate = function (e) {
    var target = e.target;
    var page = $(target).attr('href').split('#p')[1];
    var selectedFormpage = $('#formbar-page-' + page);
    setSelectedPage(e);
    $('.formbar-page').hide();
    selectedFormpage.show();
    hideSubmitButtonOnInputlessPage(selectedFormpage);
  };

  var init = function () {
    $('.formbar-tooltip').tooltip();
    $('.list-group-item').on('click', selectListGroupItem);
    $('div.formbar-form form div.tabbable ul.nav li a').click(setSelectedPage);
    $('div.formbar-outline a').click(navigate);
    initDatePicker();
    initSubmit();
    form.init();
  };

  return {
    init: init
  };

} (form);


/**
 * @function
 * 
 * when page is ready, start formbar
 *
 */
$(function () {
  formbar.init();
});
