% if field.is_readonly():
  <div class="readonlyfield">
    ${field.get_value("").replace('\n', '<br>')}
  </div>
% else:
  <textarea name="${field.name}">${field.get_value()}</textarea>
% endif
