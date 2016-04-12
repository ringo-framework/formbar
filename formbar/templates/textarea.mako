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
  % if field.renderer._config._tree.attrib.get("maxlength"):
    <div id="${field.id}_feedback" class="pull-right text-muted small"></div>
    <script>
      var text_max = ${field.renderer._config._tree.attrib.get("maxlength")}
      $('#${field.id}_feedback').html(text_max + ' ${_('characters remaining')}')

      function calcRemainingChars() {
        var text_length = $('#${field.id}').val().length;
        var text_remaining = text_max - text_length;
        $('#${field.id}_feedback').html(text_remaining + ' ${_('characters remaining')}');
      };
      $('#${field.id}').keyup(function() {
        calcRemainingChars();
      });
      calcRemainingChars();
    </script>
  % endif
% endif
