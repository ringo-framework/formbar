% for error in field.errors:
% if error != field.empty_message:
  <div class="help-block">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(error)}
  </div>
% endif
% endfor
% for warn in field.warnings:
% if warn != field.empty_message:
  <div class="help-block">
    <span class="text-warning">
        <span class="glyphicon glyphicon-warning-sign"></span>
        ${_(warn)}
    </span>
  </div>
% endif
% endfor

% if field.required or field.desired:
% if field.empty_message in field.errors:
    <div class="help-block " fieldtype="${'required' if field.required else 'desired'}">
% elif field.empty_message in field.warnings:
    <div class="help-block " fieldtype="${'required' if field.required else 'desired'}">
% else:
    <div class="help-block hidden" fieldtype="${'required' if field.required else 'desired'}">
% endif
    <span class="${'text-warning' if field.desired else ''}">
        <span class="glyphicon glyphicon-warning-sign"></span>
        ${_(field.empty_message)}
    </span>
</div>
%endif 
