% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(field.get_previous_value(""), field.get_value(""))}
    % else:
      ${field.get_value("")}
    % endif
  </div>
% else:
  <input class="form-control ${field.type}" type="text" id="${field.id}" name="${field.name}" value="${field.get_value()}"/>
% endif
