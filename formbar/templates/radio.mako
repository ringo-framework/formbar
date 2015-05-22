<%
readonly = (field.is_readonly() and "disabled") or ""
selected = field.get_value()
if not isinstance(selected, list):
  selected = [str(selected)]
else:
  selected = [str(s) for s in selected]
%>
% for num, option in enumerate(options):
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="radio-inline">
      % if option[1] in selected:
        <input type="radio" id="${field.id}-${num}" datatype="${field.get_type()}" name="${field.name}" value="${option[1]}" checked="checked" ${readonly}/>
      % else:
        <input type="radio" id="${field.id}-${num}" datatype="${field.get_type()}" name="${field.name}" value="${option[1]}" ${readonly}/>
      % endif
      ${_(option[0])}
    </label>
    % if field.renderer.align == "vertical" and num < len(options):
      <br/>
    % endif
  % elif not field.renderer.remove_filtered == "true":
    <input type="hidden" id="${field.id}" datatype="${field.get_type()}" name="${field.name}" value="${option[1]}"/>
  % endif
% endfor
