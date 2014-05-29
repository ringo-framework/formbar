% if not field.is_readonly():
  <input type="hidden" id="${field.id}" name="${field.name}" value="${field.get_value()}"/>
% else:
  <div class="readonlyfield hidden" name="${field.name}">
      ${field.get_value("")}
  </div>
% endif
