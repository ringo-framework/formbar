<label class="control-label ${field.renderer.label_position}" for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  % if field.label:
    ${_(field.label)}
  % endif
  % if field.is_required():
    <span data-toggle="tooltip" data-original-title="Required field" class="formbar-tooltip glyphicon glyphicon-asterisk"></span>
  % elif field.is_desired():
    <span data-toggle="tooltip" data-original-title="Desired field" class="formbar-tooltip glyphicon glyphicon-star"></span>
  % endif
</label>
