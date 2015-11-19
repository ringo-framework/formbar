% if not field.is_readonly():
  <input type="hidden" id="${field.id}" name="${field.name}" datatype="${field.get_type()}" value="${field.get_value()}"/>
% else:
  <div class="readonlyfield hidden" name="${field.name}" datatype="${field.get_type()}">
      ${field.get_value("")}
  </div>
% endif
