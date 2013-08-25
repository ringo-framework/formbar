% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
  </div>
% else:
  <input id="${field.id}" name="${field.name}" type="file" value=""/>
% endif
