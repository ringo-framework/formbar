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

# Preselect an entry.
# In case there is not already a selected value (eiter because the entity
# actually does have a value or the default value is set) and the renderer is
# configured to preselect an entry from the options.
if not selected and field.renderer.selected:
  selected_idx = int(field.renderer.selected)
  if len(filterd_values) >= abs(selected_idx):
    selected_value = filterd_values[selected_idx]
    selected = selected_value

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
      % if str(option[1]) == str(selected):
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
