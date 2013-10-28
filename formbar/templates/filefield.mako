% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
  </div>
% else:
  <input class="form-control" id="${field.id}" name="${field.name}" type="file" value=""/>
% endif
