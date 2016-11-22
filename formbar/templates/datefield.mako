<%
if field._form._locale == "de":
  placeholder = "TT.MM.JJJJ"
else:
  placeholder = "YYYY-MM-DD"
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
  <div class="input-group date date formbar-datepicker">
    <input type="text"  name="${field.name}" value="${field.get_value()}" datatype="${get_field_type(field)}"
    class="form-control ${get_field_type(field)}" placeholder="${placeholder}"><span class="input-group-addon"><i class="glyphicon glyphicon-th"></i></span>
  </div>
% endif
