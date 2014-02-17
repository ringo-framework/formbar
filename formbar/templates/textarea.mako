% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(field.get_previous_value(""), field.get_value(""))}
    % else:
      ${field.get_value("")}
    % endif
  </div>
% else:
  <textarea class="form-control" id="${field.id}" name="${field.name}" rows="${field.renderer.rows}">${field.get_value()}</textarea>
% endif
