% if field.is_readonly():
  <div class="readonlyfield">
  </div>
% else:
  <input id="${field.id}" name="${field.name}" type="file" value=""/>
% endif
