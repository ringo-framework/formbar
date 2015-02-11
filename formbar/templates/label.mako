<label class="control-label ${field.renderer.label_position} ${field.renderer.render_type}" for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  % if field.label:
    ${_(field.label)}
  % endif
  % if field.is_required():
    <span data-toggle="tooltip" data-original-title="${_('Required field')}" class="formbar-tooltip glyphicon glyphicon-asterisk"></span>
  % endif
</label>
