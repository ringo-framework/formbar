% if field.is_readonly():
  <div class="readonlyfield">
    ${field.get_value("")}
  </div>
% else:
  <input type="password" name="${field.name}" value="${field.get_value()}"/>
% endif
