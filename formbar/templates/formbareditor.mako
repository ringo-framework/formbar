<%
pages = [x.attrib.get('id') for x in field._form._config._parent.get_elements("form")]
%>
<ul id="tabs" class="nav nav-tabs" data-tabs="tabs">
  <li class="active"><a id="formbar-editor-tab" href="#formbar-editor" data-toggle="tab">${_('Editor')}</a></li>
  %for page in pages:
    <li><a class="formbar-preview-tab" id="formbar-preview-tab-${page}" href="#formbar-preview-${page}" data-toggle="tab">${_('Preview')} "${page}"</a></li>
  %endfor
</ul>
<div id="formbareditor-tab-content" class="tab-content">
  <div class="tab-pane active" id="formbar-editor">
    % if field.is_readonly():
      <div class="readonlyfield" name="${field.name}">
        % if field.get_previous_value() is not None:
          ${renderer._render_diff(field.get_previous_value(""), field.get_value(""))}
        % else:
          ${field.get_value("")}
        % endif
      </div>
    % else:
      <form id="" action="${renderer.url}" target="preview-iframe">
        <textarea class="form-control" id="${field.id}" name="${field.name}" rows="${field.renderer.rows}">${field.get_value()}</textarea>
      </form>
    % endif
  </div>
  %for page in pages:
    <div class="tab-pane formbar-preview-window" id="formbar-preview-${page}">
    <p>Preview ${page}</p>
    </div>
  %endfor
</div>
<p><small><strong>Note:</strong> ${_('This is just a basic editor for formbar forms. The preview of the forms will have no outline, no dynamic nor will show application specific fields. Instead of those the default textfield will be rendered.')} </small></p>

<script>
//$('#${field.id}').focus(function(e) {
//  var definition = $('#${field.id}').val();
//  var pages = $(definition).find("form");
//  alert(pages.length);
//});
$('.formbar-preview-tab').click(function(e) {
  var definition = getFormDefinition();
  var tmp = $(this).attr("id").split("-");
  var formid = tmp[tmp.length-1];
  // Dynamically create a form to submit the form definition
  // var tmpform = $('<form action="${renderer.url}" method="POST" target="_blank"></form>')
  // tmpform.append($('<input type="hidden" name="definition"/>').attr("value", getFormDefinition()))
  // tmpform.append($('<input type="hidden" name="csrf_token"/>').attr("value", "${field._form._request.session.get_csrf_token()}"))
  // tmpform.appendTo('body').submit().remove();
  var renderered_form = renderPreview(definition, formid); 
  $('#formbar-preview-'+formid).html(renderered_form);

});

function getFormDefinition() {
  var definition = $('#${field.id}').val();
  return definition;
}

function renderPreview(definition, formid) {
  var result = null;
  $.ajax({
      type: "POST",
      async: false,
      url: "${renderer.url}",
      data: {definition: definition, formid: formid, csrf_token: "${field._form._request.session.get_csrf_token()}"},
      success: function (data) {
          if (data.success) {
              result = data.data.form
          } else {
              console.log(data.params.msg);
              result = data
          }
      }
  });
  return result;
}

</script>
