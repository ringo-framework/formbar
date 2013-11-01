<label class="control-label" for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  % if field.label:
    ${_(field.label)}
  % endif
  % if field.is_required():
    <span data-toggle="tooltip" data-original-title="Required fa_field" class="formbar-tooltip glyphicon glyphicon-asterisk"></span>
  % endif
</label>
