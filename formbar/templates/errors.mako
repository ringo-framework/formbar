% for rule in field.get_error_rules():
  <div class="help-block ${not (rule.result == None or rule.result )or "hidden"}">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(rule.msg)}
  </div>
% endfor
% for rule in field.get_warning_rules():
  ## Hide the error message initialy if the field is not missing e.g the field
  ## is not active in a conditional. Mark this field in the DOM to be able to
  ## toggle the error message in case a conditional becomes enabled.
  ## TODO: Should we better use the "active" attribute of the renderer here?
  <div class="help-block ${field.is_missing() or "hidden"}" desired="${field.is_desired()}">
    <span class="text-warning">
    <span class="glyphicon glyphicon-warning-sign"></span>
    ${_(rule.msg)}
    </span>
  </div>
% endfor
