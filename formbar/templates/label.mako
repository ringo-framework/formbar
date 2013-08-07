<label for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  % if field.label:
    ${_(field.label)}
  % endif
  % if field.is_required():
    <a href="#" data-toggle="tooltip" class="formbar-tooltip" data-original-title="Required fa_field"><i class="icon-asterisk"></i></a>
  % endif
</label>
