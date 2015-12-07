<%
if field._form._locale == "de":
  placeholder = "TT.MM.JJJJ"
else:
  placeholder = "YYYY-MM-DD"
%>
% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(field.get_previous_value(""), field.get_value(""))}
    % else:
      ${field.get_value("")}
    % endif
  </div>
% else:
  <div class="input-group date date formbar-datepicker">
    <input type="text"  name="${field.name}" value="${field.get_value()}" datatype="${field.get_type()}"
    class="form-control ${field.type}" placeholder="${placeholder}"><span class="input-group-addon"><i class="glyphicon glyphicon-th"></i></span>
  </div>
% endif
