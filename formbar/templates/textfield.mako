% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(_(field.get_previous_value("")), _(field.get_value("")))}
    % else:
      ${_(field.get_value(""))}
    % endif
  </div>
% else:
  <input class="form-control ${field.type}" type="text" id="${field.id}" name="${field.name}" value="${field.get_value()}" ${field.autofocus and 'autofocus'}/>
% endif
