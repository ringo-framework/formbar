% if field.readonly:
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(_(field.get_previous_value("")), _(field.get_value("")))}
    % else:
      ${field.get_value("")}
    % endif
  </div>
  <input class="form-control ${get_field_type(field)}" type="hidden" datatype="${get_field_type(field)}" id="${field.id}" name="${field.name}" value="${field.get_value()}"/>
% else:
  <input ${'' if renderer._active else 'readonly=readonly '} class="form-control ${get_field_type(field)}" type="text" datatype="${get_field_type(field)}" id="${field.id}" name="${field.name}" value="${field.get_value()}" ${field.autofocus and 'autofocus'}/>
% endif
