<label for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  % if field.label:
    ${_(field.label)}
  % endif
  % if field.is_required():
    <i data-toggle="tooltip" data-original-title="Required fa_field" class="formbar-tooltip icon-asterisk"></i>
  % endif
</label>
