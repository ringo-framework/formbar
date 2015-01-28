% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
  </div>
% else:
  <input class="form-control" type="password" id="${field.id}" autocomplete="off" name="${field.name}"/>
% endif
