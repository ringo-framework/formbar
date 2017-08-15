<%
if field._form._locale == "de":
  placeholder = "TT.MM.JJJJ HH:MM:SS"
else:
  placeholder = "YYYY-MM-DD HH:MM:SS"
%>
% if field.readonly:
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(field.get_previous_value(""), field.get_value(""))}
    % else:
      ${field.get_value("")}
    % endif
  </div>
% else:
  <div class="input-group formbar-datetimepicker">
    <input type="text"  name="${field.name}" value="${field.get_value() or ''}" datatype="${get_field_type(field)}"
    class="form-control ${get_field_type(field)}" placeholder="${placeholder}"><span class="input-group-addon"><i class="fa fa-calendar" aria-hidden="true"></i> <i class="fa fa-clock-o" aria-hidden="true"></i></span>
  </div>
% endif
