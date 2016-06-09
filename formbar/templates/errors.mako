% for error in field.get_errors():
% if error != field.empty_message:
  <div class="help-block">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(error)}
  </div>
% endif
% endfor
% for warn in field.get_warnings():
% if warn != field.empty_message:
  <div class="help-block">
    <span class="text-warning">
        <span class="glyphicon glyphicon-warning-sign"></span>
        ${_(warn)}
    </span>
  </div>
% endif
% endfor

% if field.is_required or field.is_desired:
% if field.empty_message in field.get_errors():
    <div class="help-block " fieldtype="${'required' if field.is_required else 'desired'}">
% elif field.empty_message in field.get_warnings():
    <div class="help-block " fieldtype="${'required' if field.is_required else 'desired'}">
% else:
    <div class="help-block hidden" fieldtype="${'required' if field.is_required else 'desired'}">
% endif
    <span class="${'text-warning' if field.is_desired else ''}">
        <span class="glyphicon glyphicon-warning-sign"></span>
        ${_(field.empty_message)}
    </span>
</div>
%endif 
