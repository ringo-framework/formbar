/* Formbar rewrite */

/** 
 * @function
 * reduce is defined as a shortcut to [].reduce()
 */
var reduce = Function.prototype.call.bind([].reduce);
var map = Function.prototype.call.bind([].map);

    /** 
     * @module
     * Conatins the mechanics for evaluating fields and communication results
     * from the server back to the application. Is used by the form-component
     *  
     * @public
     * @function
     * 
     * init - initialization of the engine
     * onFieldChange - eventhandler 
     * communicates field-changes to the server and evaluates rules
     */
var ruleEngine = function () {
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
    var checkFields = function (rule, expression, callBack, divId) {
        var form = $("#" + divId).closest("form");
        var eval_url = $(form).attr("evalurl");
        var ruleParam = "?rule=" + encodeURIComponent(expression);
        $.ajax({
            type: "GET",
            url: eval_url + ruleParam,
            success: function (data) {
                callBack(data.data, divId, rule);
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
    var parseExpression = function (expression, currentValues) {
        return expression.split(" ").map(function (token) {
            if (token[0] === '$') {
                var currentValue = convertValue(currentValues[token.replace("$", "")]);
                var token = currentValue;
                if (Array.isArray(currentValue)) {
                    token = JSON.stringify(currentValue).replace(/"/g, "'");
                }
            }
            return token;
        }).join("  ");
    }


    /**
     * @function
     * 
     * delivers a parsable for brabbel according to datatype
     * 
     * @param {Object} currentValue
     * 
     */
    var convertValue = function(currentValue){
        var v = currentValue.value
        if (currentValue.state === 'inactive') return "None";
        switch(currentValue.datatype){
            case 'date':
            case 'text':
            case 'string':
                return (!stringContainsArray(v))?"'"+v.replace(/\n/g,'')+"'":v;
            default:
                return currentValue.value || "None";
        }

    }

    /**
     * @function
     * 
     * looks for '[' as a sign for an array value
     * 
     * @param {string} currentValue
     * 
     */
    var stringContainsArray = function(currentValue){
        return currentValue.indexOf('[') !== -1;
    }

    /**
     * @function 
     * 
     * onFieldChange is exported.
     * It is used as a callable for field-change-events
     * 
     * @param {string} name - the name of the field / variable which is changed
     * 
     * @param {Object} currentValues - holds the current state of all fields
     * 
     * @param {function} callBack - a function to call back after evaluation
     * 
     */
    var onFieldChange = function (name, currentValues, callback) {
        if (conditionals[name]) {
            var rulesForField = conditionals[name];
            Object.keys(rulesForField).forEach(function (k) {
                var rule = rulesForField[k].expr;
                checkFields(rule, parseExpression(rule, currentValues), callback, k);
            });
        }
        return true;
    }

    /**
     * @function 
     * 
     * onFieldChange is exported.
     * It is used as a callable for field-change-events
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     * @param {string} currentValues - holds the current state of all fields
     * 
     * @param {string} callBack - a function to call back after evaluation
     *
     * @param {rule} rule - the current rule to be evaluated
     *  
     */
    var evaluateRule = function(fieldname, currentValues, callback, rule){
        checkFields(rule, parseExpression(rule, currentValues), callback, fieldname);
    }

    var init = function () {
        conditionals = scanConditionals();
    };
    return {
        init: init,
        onFieldChange: onFieldChange,
        evaluateRule: evaluateRule
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
        return !(key.charCode !== 0 && key.charCode !== point && key.charCode !== minus && (key.charCode < zero || key.charCode > nine));
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
 * and ressetting of values, evaluating the rulesForField and promote changes to
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
                $("input[name='" + fname + "']:checked").each(function () {
                    result.push($(this).val());
                });
                break;
            case "radio":
                result = $("input[name='" + fname + "']:checked").val();
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
                    $("[name='" + fieldName + "']:checked").each(function (i, x) { $(x).prop("checked", false); })
                    break;
                case "radio":
                    $("input[name='"+ fieldName +"'][value='']").prop("checked",true)
                    break;
                default:
                    $("input[name='" + fieldName + "']").val("");
                    break;
            }
        } else if (field.tagName === 'SELECT') {
            $("select[name='" + fieldName + "']").val("");
        } else if (field.tagName === 'TEXTAREA') {
            $("textarea[name='" + fieldName + "']").val("");
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
                    $("input[name='"+fieldName+"']:checked").each(function(){$(this).prop('checked', false)})
                    formFields[fieldName].value.forEach(function (x) { $("[name='"+fieldName+"'][value='" + x + "']").prop("checked", true); });
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
        } else if (field.tagName === 'TEXTAREA') {
            $("textarea[name='" + fieldName + "']").val(formFields[fieldName].value);
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
     * extract rules from a div
     * 
     * @param {Object} element - selected div
     * 
     */
    var getRules = function(element){
        var rules = element.getAttribute("rules").split(";");
        return rules.map(function(x){
            var expr = x.split(",");
            var rule = expr[0];
            var type = expr[1];
            return {
                "expr": rule,
                "type": type,
            };
        });
    }

    /**
     * @function
     * 
     * scans every form-group and gathers every INPUT.
     * holds state ("active/inactive", value, required, desired) information of
     * these elements. Acts as a simple model.
     *
     */
    var scanComponents = function () {
        return reduce($(".form-group"), function (o, x) {
            var name = $(x).attr("formgroup");
            if (name) {
                var state = ($(x).hasClass("active")) ? "active" : "inactive";
                var element = scanForContentElements(x);
                var value = getFieldValue(element);
                var desired = x.getAttribute("desired");
                var required = x.getAttribute("required");
                var datatype = (element)?element.getAttribute("datatype"):undefined;
                var rules = getRules(x);
                o[name] = {
                    'name': name,
                    'state': state,
                    'value': value,
                    'desired': desired,
                    'required': required,
                    'datatype': datatype,
                    'rules': rules
                };
            }
            return o;
        }, {});
    };


    /**
     * @function
     * 
     * looks for any content element
     *
     * @param {Object} x - DOM-Node
     */
    scanForContentElements = function(x){
        return $(x).find("input")[0]||$(x).find("textarea")[0]||$(x).find("select")[0];
    }

    /**
     * @function
     * 
     * is called after evaluation of rulesForField.
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
    var toggleConditional = function (result, divId, rule) {
        var element = $("#" + divId);
        if (result) {
            element.addClass("active");
            element.removeClass("inactive");
        } else {
            element.addClass("inactive");
            element.removeClass("active");
        }
        if (element.attr("type") === "readonly"){
            handleReadOnly(result, element);
        } else {
            handleVisbility(result, element);
        } 

    }

    var handleVisbility = function(result, element){
        if (result){
            element.fadeIn("1500").removeClass("hidden");
        } else {
            element.fadeOut("1500").addClass("hidden");
        }
        handleReadOnly(result, element);
    }

    var findFieldsToUpdate= function(div){
        return map(div.find(".form-group"), (function (x) {
            return x.getAttribute("formgroup");
        }));
    }

    /**
     * @function
     * 
     * in case of a negative result we have to deactivate some fields wherein the values are deleted
     * 
     * in case of a positive result we have to activate the fields again and reset status quo ante
     * 
     * @param {Object} result - evaluation result of the rule
     *  
     * @param {Object} div - selected div
     * 
     */
    var handleReadOnly = function (result, div) {
        fieldsToUpdate = findFieldsToUpdate(div);

        fieldsToUpdate.forEach(function (fieldName) {
            var field = formFields[fieldName];
            var oldState = field.state;
            var newState = oldState;
            if (result == true && oldState == "inactive") {
                resetFieldValue(fieldName, formFields);
                $("[name='"+fieldName+"']").map(function(i,x){ if (x.type==='text' || x.tagName==='TEXTAREA') x.removeAttribute("readonly"); })
                newState = "active";
                if (!field.value) activateDesired(fieldName);
            }
            if (result == false && oldState == "active") {
                if (div.closest(".formbar-conditional").attr("reset-value") == "true") {
                    clearFieldValue(fieldName);
                }
                $("[name='"+fieldName+"']").map(function(i,x){ if (x.type==='text' || x.tagName==='TEXTAREA') x.setAttribute("readonly","readonly"); })
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

    /**
     * @function
     * 
     * handles visuals
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var deactivateRequired = function (fieldName) {
        var field = formFields[fieldName];
        if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
            $(".form-group[formgroup='" + fieldName + "']").removeClass("has-warning");
        }
        if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-error")) {
            $(".form-group[formgroup='" + fieldName + "']").removeClass("has-error");
        }
        $(".form-group[formgroup='" + fieldName + "']").find(".help-block").addClass("hidden");

    }

    /**
     * @function
     * 
     * handles visuals
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var activateRequired = function (fieldName) {
        var field = formFields[fieldName];
        $(".form-group[formgroup='" + fieldName + "']").find(".help-block").addClass("hidden");
        if (field.required === "True" && !$(".form-group[formgroup='" + fieldName + "']").hasClass("has-error")) {
            if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
                $(".form-group[formgroup='" + fieldName + "']").removeClass("has-warning");
            }
            $(".form-group[formgroup='" + fieldName + "']").addClass("has-error");
            $(".form-group[formgroup='" + fieldName + "']").find(".help-block[fieldtype='required']").removeClass("hidden");
        }
        $(".form-group[formgroup='" + fieldName + "']").find(".help-block[fieldtype='required']").removeClass("hidden");
    }

    /**
     * @function
     * 
     * handles visuals
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var deactivateDesired = function (fieldName) {
        var field = formFields[fieldName];
        if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
            $(".form-group[formgroup='" + fieldName + "']").removeClass("has-warning");
        }
        if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-error")) {
            $(".form-group[formgroup='" + fieldName + "']").removeClass("has-error");
        }
        $(".form-group[formgroup='" + fieldName + "']").find(".help-block").addClass("hidden");    
    }

    /**
     * @function
     * 
     * handles visuals
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var activateDesired = function (fieldName) {
        var field = formFields[fieldName];
        $(".form-group[formgroup='" + fieldName + "']").find(".help-block").addClass("hidden");
        if ($(".form-group[formgroup='" + fieldName + "']").hasClass("has-error")) {
            $(".form-group[formgroup='" + fieldName + "']").removeClass("has-error");
        }
        if (field.desired === "True" && !$(".form-group[formgroup='" + fieldName + "']").hasClass("has-warning")) {
            $(".form-group[formgroup='" + fieldName + "']").addClass("has-warning");
            $(".form-group[formgroup='" + fieldName + "']").find(".help-block[fieldtype='desired']").removeClass("hidden");
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
        ruleEngine.onFieldChange(fieldName, formFields, function (data, divId, rule) {
            toggleConditional(data, divId, rule);
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
        setStateForCurrentField(target.name);
        triggerChange(target.name);
    };


    /**
     * @function
     * 
     * evaluate every rule attached to a given element
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var evaluateRules = function(element){
        element.rules.forEach(function(rule){
            ruleEngine.evaluateRule(element.name, formFields, function (result, divId, rule) {
                messageDiv=$("[rule='"+rule+"']");
                if (result) {
                    if(messageDiv.hasClass("hidden")=== false) messageDiv.addClass("hidden");
                } else {
                    if(messageDiv.hasClass("hidden")=== true) messageDiv.removeClass("hidden");
                }

            }, rule.expr);
        });
    }

    /**
     * @function
     * 
     * handles visuals
     * 
     * @param {string} fieldname - the name of the field / variable which is changed
     * 
     */
    var setStateForCurrentField = function (fieldName) {
        var element = formFields[fieldName];
        if (!element.value.length && element.desired === "True") activateDesired(fieldName);
        if (!element.value.length && element.required === "True") activateRequired(fieldName);
        if (!!element.value.length && element.desired === "True") deactivateDesired(fieldName);
        if (!!element.value.length && element.required === "True") deactivateRequired(fieldName);
    }

    /**
     * @function
     * 
     * sets the global listener for changes in INPUT / SELECT / TEXTAREA
     *
     */
    var setListener = function () {
        var timeOutID;
        var changeEvent = function(e){
            var div = $(e.target);
            var fieldName = e.target.name;
            if (formFields[fieldName].state==='inactive'){
                if (div.closest(".formbar-conditional").attr("reset-value") == "true") {
                   clearFieldValue(fieldName);
                } else {
                    resetFieldValue(fieldName, formFields);
                }
            } else {
                inputChanged(e);
            }
        };
        $("div.formbar-form").on("keyup", function(e) {
            switch (e.target.tagName) {
                case 'INPUT':
                case 'TEXTAREA':
                    if(timeOutID) clearTimeout(timeOutID)
                    timeOutID = setTimeout(function(){
                        changeEvent(e);
                    }, 400);
                    break;
                default:
                    break;
            }
        });
        $("div.formbar-form").on("change", function (e) {
            switch (e.target.tagName) {
                case 'INPUT':
                case 'SELECT':
                case 'TEXTAREA':
                    changeEvent(e);
                    break;
                default:
                    break;
            }
        });
    };

    var init = function () {
        initInputFilters();
        formFields = scanComponents();
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
    /**
     * @function 
     * retrieves the browserlanguage from the navigator oject of the browser
     *
     */
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
     * determines the dateformat based on te browserlanguage. Only german and
     * ISO 8601 is supported.
     *
     */
    var getDateFormat = function getDateFormat(browserLanguage) {
        if (browserLanguage.search("de") > -1) {
            return "dd.mm.yyyy"
        } else {
            return "yyyy-mm-dd"
        }
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
        var lastpage = $('.formbar-outline a.selected').attr("formbar-lastpage");
        if (selected_formpage.length > 0) {
            hideSubmitButtonOnInputlessPage(selected_formpage);
        }
        if (lastpage == "true") {
            var button = $(".formbar-form button[value='nextpage']");
            button.hide();
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
        var dateFormat = getDateFormat(browserLanguage);
        $('.formbar-datepicker').datepicker({
            language: browserLanguage,
            format: dateFormat,
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
     * Toggle the special submit and next submit button if this is the
     * last page.
     *
     */
    var toggleNextPageSubmit = function (e) {
        // If selected page is the last page then hide the submitnext
        // button. Otherwise show it.
        var target = e.target;
        var lastpage = $(target).attr('formbar-lastpage');
        var button = $(".formbar-form button[value='nextpage']");
        if (button) {
            if (lastpage == "true") {
                console.log("Hide");
                button.hide();
            } else {
                console.log("Show");
                button.show();
            }
        }
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

        // Hack! Force a resize event on page change. This will trigger
        // repainting the page. This hack fixes issues with sizes of elements
        // on hiden pages (E.g dygraphs). Those element might have a size of 0
        // because the elements where hidden. Triggering a resize of the
        // window after the pagehas become visible will repaint the page with
        // correct sizes.
        var evt = document.createEvent('UIEvents');
        evt.initUIEvent('resize', true, false,window,0);
        window.dispatchEvent(evt);

        hideSubmitButtonOnInputlessPage(selectedFormpage);
        toggleNextPageSubmit(e);
    };

    var init = function () {
        $('.formbar-tooltip').tooltip();
        $('.list-group-item').on('click', selectListGroupItem);
        $('div.formbar-form form div.tabbable ul.nav li a').click(setSelectedPage);
        $('div.formbar-outline a').click(navigate);
        $('div.formbar-form form').not(".disable-double-submit-prevention").preventDoubleSubmission();
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
}

/* Method to calculate the remaining chars in the given textarea. Textarea is
 * identified by its id. See textarea.mako for more details. */
function calcRemainingChars(id, msg) {
    var text_max = $('#'+id).attr("maxlength");
    var text = $('#'+id).val()
    // Handle newlines in a special way and count the as two chars.
    var num_newlines = text.split("").filter(function(x){return x === '\n'}).length
    var text_length = text.length + num_newlines;
    var text_remaining = text_max - text_length;
    $('#'+id+'_feedback').html(text_remaining + ' ' + msg);
}
