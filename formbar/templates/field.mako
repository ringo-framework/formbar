## Label
<label for="${field.name}">
  % if field.number:
    <sup>(${field.number})</sup>
  % endif
  ${field.label}
  % if field.is_required():
    <a href="#" data-toggle="tooltip" class="formbar-tooltip" data-original-title="Required fa_field"><i class="icon-asterisk"></i></a>
  % endif
</label>

## field
## TODO: Add escaping here! "h" for mako escaping is not available here for
## unknow reasons.
% if field.is_readonly():
  <div class="readonlyfield">
    ${field._fa_field.render() or "&nbsp;"}
  </div>
% else:
  ${field._fa_field.render()}
% endif

## Errors
% for error in field.get_errors():
  <div class="text-error">
    <i class="icon-exclamation-sign"></i>
    ${error}
  </div>
% endfor

## Helptexts
% if field.help is not None:
<div class="text-help">
  <i class="icon-info-sign"></i>
  ${field.help}
</div>
% endif
