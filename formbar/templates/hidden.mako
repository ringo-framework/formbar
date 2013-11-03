% if not field.is_readonly():
  <input type="hidden" id="${field.id}" name="${field.name}" value="${field.get_value()}"/>
% endif
