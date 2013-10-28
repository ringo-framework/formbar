% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    ${field.get_value("").replace('\n', '<br>')}
  </div>
% else:
  <textarea class="form-control" id="${field.id}" name="${field.name}">${field.get_value()}</textarea>
% endif
