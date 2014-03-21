<%
if field._tree.attrib.get('expr'):
  css = "formbar-evaluate"
else:
  css = ""
%>
<div class="readonlyfield ${css}" id="${field.id}" expr="${field._tree.attrib.get('expr')}">
  ${field.get_value("")}
</div>
