% for rule in field.get_error_rules():
  <div class="help-block ${not rule.result or "hidden"}">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(rule.msg)}
  </div>
% endfor
% for rule in field.get_warning_rules():
  <div class="help-block ${not rule.result or "hidden"}" desired="${rule.desired}" required="${rule.required}">
    <span class="text-warning">
    <span class="glyphicon glyphicon-warning-sign"></span>
    ${_(rule.msg)}
    </span>
  </div>
% endfor
