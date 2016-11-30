<%
if field._tree.attrib.get('expr'):
  css = "formbar-evaluate"
else:
  css = ""
%>
<div class="readonlyfield ${css}" id="${field.id}" expr="${field._tree.attrib.get('expr')}">
  % if renderer._config.showrawvalue == "true":
    <% 
    if isinstance(field.value, list):
      value = ", ".join([_(i) for i in field.value])
    else:
      value = _(field.value)
    %>
    ${value}
  % else:
    ${_(field.get_value(""))}
  % endif
</div>
