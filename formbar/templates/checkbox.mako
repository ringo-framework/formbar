<br>
<%
readonly = (field.is_readonly() and "disabled") or ""
%>
% for option in options:
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="checkbox-inline">
      <input type="checkbox" id="${field.id}" name="${field.name}" value="${option[1]}" ${readonly}/>
      ${option[0]}
    </label>
  % elif not field.renderer.remove_filtered == "true":
    <input type="hidden" id="${field.id}" name="${field.name}" value="${option[1]}"/>
  % endif
% endfor
