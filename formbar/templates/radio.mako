<%
readonly = (field.readonly and "disabled") or ""
selected = field.get_value()
if isinstance(selected, list):
  if len(selected) > 1:
    raise TypeError("There can not be multiple selected values in a radio renderer!")
  elif len(selected) == 0:
    selected = None
  else:
    selected = selected[0]

  ## Check if the selection value is among the filtered options. If not the 
filterd_values = [str(o[1]) for o in options if o[2]]
if str(selected) in filterd_values:
  selected = str(selected)
else:
  selected = ""
%>

% for num, option in enumerate(options):
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="radio-inline">
      % if option[1] == selected:
        <input type="radio" id="${field.id}-${num}" datatype="${get_field_type(field)}" name="${field.name}" value="${option[1]}" checked="checked" ${readonly}/>
        ## Render a hidden field for selected readonly values to make sure the
        ## value is actually submitted.
        % if readonly:
          <input type="hidden" id="${field.id}-${num}" datatype="${get_field_type(field)}" name="${field.name}" value="${option[1]}"/>
        % endif
      % else:
        <input type="radio" id="${field.id}-${num}" datatype="${get_field_type(field)}" name="${field.name}" value="${option[1]}" ${readonly}/>
      % endif
      ${_(option[0])}
    </label>
    % if field.renderer.align == "vertical" and num < len(options):
      <br/>
    % endif
  % endif
% endfor
