<%
readonly = (field.is_readonly() and "disabled") or ""
## TODO: field should return a field specific value. So we do not need to
## handle the special case here if there is no value set. (ti) <2015-07-07
## 14:50> 
selected = field.get_value() or []
%>
% for num, option in enumerate(options):
  ## Depending if the options has passed the configured filter the
  ## option will be visible or hidden
  % if option[2]:
    <label class="checkbox-inline">
      % if option[1] in selected:
        <input type="checkbox" id="${field.id}-${num}" name="${field.name}" value="${option[1]}" checked="checked" ${readonly}/>
        ## Render a hidden field for selected readonly values to make sure the
        ## value is actually submitted.
        % if readonly:
          <input type="hidden" id="${field.id}-${num}" name="${field.name}" value="${option[1]}"/>
        % endif
      % else:
        <input type="checkbox" id="${field.id}-${num}" name="${field.name}" value="${option[1]}" ${readonly}/>
      % endif
      ${_(option[0])}
    </label>
    % if field.renderer.align == "vertical" and num < len(options):
      <br/>
    % endif
    ## Prevent loosing already set values. In case a already selected value is
    ## filtered for some reason than render a hidden input element with the
    ## value except the user explicit sets the "remove_filtered" config var.
  % elif not field.renderer.remove_filtered == "true" and option[1] in selected:
    <input type="hidden" id="${field.id}" name="${field.name}" value="${option[1]}"/>
  % endif
% endfor
## Hack! Empyt value to allow deselecting all options.
% if not field.is_readonly():
  <input style="display:none" type="checkbox" name="${field.name}" value="" checked="checked"/>
% endif
