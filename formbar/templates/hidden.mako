% if not field.is_readonly():
  <input type="hidden" id="${field.id}" name="${field.name}" datatype="${get_field_type(field)}" value="${field.get_value()}"/>
% else:
  <div class="readonlyfield hidden" name="${field.name}" datatype="${get_field_type(field)}">
      ${field.get_value("")}
  </div>
% endif
