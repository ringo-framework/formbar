% if field.readonly:
  <div class="readonlyfield" name="${field.name}">
    ${field.get_value("")}<span class="glyphicon ${renderer.icon or 'glyphicon-euro'}"></span>
  </div>
% else:
  <div class="input-group">
    <input class="form-control currency" id="${field.id}" type="text" name="${field.name}" value="${field.get_value()}" placeholder="${field.placeholder or '1.234,50'}"/>
    <div class="input-group-addon">
      <span class="glyphicon ${renderer.icon or 'glyphicon-euro'}"></span>
    </div>
  </div>
% endif
