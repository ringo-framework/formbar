% if field.is_readonly():
  <div class="readonlyfield">
    ${field._fa_field.render() or "&nbsp;"}
  </div>
% else:
  ${field._fa_field.render()}
% endif
