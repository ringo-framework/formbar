% for error in field.get_error_rules():
  <div class="help-block ${'' if field.has_errors else 'hidden'}" type="error" required="${field.is_required()}">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(error)}
  </div>
% endfor
% for warning in field.get_warning_rules():
  <div class="help-block ${'hidden' if not(field.has_warnings ) else ''}" type="error" desired="${field.is_desired()}">
    <span class="text-warning">
    <span class="glyphicon glyphicon-warning-sign"></span>
    ${_(warning)}
    </span>
  </div>
% endfor
