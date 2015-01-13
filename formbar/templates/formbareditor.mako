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
      <textarea class="form-control" id="${field.id}" name="${field.name}" rows="${field.renderer.rows}">${field.get_value()}</textarea>
      <div id="formbareditor" style="height:350px;position:relative;"></div>
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
ace.require("ace/ext/language_tools");
##//Add custom snippets
##ace.config.loadModule('ace/ext/language_tools', function () {
##  var snippetManager = ace.require('ace/snippets').snippetManager; 
##  ace.config.loadModule('ace/snippets/xml', function(m) {
##    if (m) { 
##      m.snippets.push({ 
##        content: '${"${1:test}"}.this is custom snippet text!', 
##        tabTrigger: 'xxx'
##      });
##      snippetManager.register(m.snippets, m.scope); 
##    }
##  });
##});

// Initialisation of the formbar editor
var editor = ace.edit("formbareditor");
editor.getSession().setMode("ace/mode/xml");
editor.getSession().setTabSize(2);
editor.setOptions({
  enableBasicAutocompletion: true,
  enableSnippets: true
});

// Handle exchanging values between the ace editor window and the textarea
// field.
var textarea = $('textarea[name="${field.name}"]').hide();
editor.getSession().setValue(textarea.val());
editor.getSession().on('change', function(){
  textarea.val(editor.getSession().getValue());
});

$('.formbar-preview-tab').click(function(e) {
  var definition = getFormDefinition();
  var tmp = $(this).attr("id").split("-");
  var formid = tmp[tmp.length-1];
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
      url: "${field._form._url_prefix}${renderer.url}",
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
