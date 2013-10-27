% if field.is_readonly():
  <div class="readonlyfield">
    ${field.get_value("")}
  </div>
% else:
  <input class="formbar-datepicker form-control" type="text" name="${field.name}" value="${field.get_value()}"/>
% endif
