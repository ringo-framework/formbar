% for rule in field.get_error_rules():
  <div class="help-block ${'' if field.has_errors else 'hidden'}" type="error" rule="${rule._expression}" required="${field.is_required()}">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(rule.msg)}
  </div>
% endfor
% for rule in field.get_warning_rules():
  <div class="help-block ${'hidden' if not(field.has_warnings ) else ''}" type="error" rule="${rule._expression}" desired="${field.is_desired()}">
    <span class="text-warning">
    <span class="glyphicon glyphicon-warning-sign"></span>
    ${_(rule.msg)}
    </span>
  </div>
% endfor
