% if field.is_readonly():
  <div class="readonlyfield">
    ${field.get_value("") or "&nbsp;"}
  </div>
% else:
  <input type="text" name="${field.name}" value="${field.get_value()}"/>
% endif
