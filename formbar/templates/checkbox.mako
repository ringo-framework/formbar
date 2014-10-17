<%
readonly = (field.is_readonly() and "disabled") or ""
selected = field.get_value()
%>
% for num, option in enumerate(options):
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="checkbox-inline">
      % if option[1] in selected:
        <input type="checkbox" id="${field.id}-${num}" name="${field.name}" value="${option[1]}" checked="checked" ${readonly}/>
      % else:
        <input type="checkbox" id="${field.id}-${num}" name="${field.name}" value="${option[1]}" ${readonly}/>
      % endif
      ${_(option[0])}
    </label>
    % if field.renderer.align == "vertical" and num < len(options):
      <br/>
    % endif
  % elif not field.renderer.remove_filtered == "true":
    <input type="hidden" id="${field.id}" name="${field.name}" value="${option[1]}"/>
  % endif
% endfor
<input style="display:none" type="checkbox" name="${field.name}" value="" checked="checked"/>
