% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    <a href="mailto:${field.get_value("")}">${field.get_value("")}</a>
  </div>
% else:
  <div class="input-group">
    <input class="form-control email" id="${field.id}" type="text" name="${field.name}" value="${field.get_value()}" placeholder="mail@example.com"/>
    <div class="input-group-addon">
      <span class="glyphicon glyphicon-envelope"></span>
    </div>
  </div>
% endif
