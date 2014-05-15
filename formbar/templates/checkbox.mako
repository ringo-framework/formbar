<%
readonly = (field.is_readonly() and "disabled") or ""
%>
% for num, option in enumerate(options):
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="checkbox-inline">
      <input type="checkbox" id="${field.id}-${num}" name="${field.name}" value="${option[1]}" ${readonly}/>
      ${option[0]}
    </label>
    % if field.renderer.align == "vertical" and num < len(options):
      <br/>
    % endif
  % elif not field.renderer.remove_filtered == "true":
    <input type="hidden" id="${field.id}" name="${field.name}" value="${option[1]}"/>
  % endif
% endfor
