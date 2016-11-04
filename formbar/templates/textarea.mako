% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(renderer.nl2br(field.get_previous_value("")), frenderer.nl2br(ield.get_value("")))}
    % else:
      ${renderer.nl2br(field.get_value(""))}
    % endif
  </div>
% else:
  <textarea  datatype="${field.get_type()}" ${'' if renderer._active else 'readonly=readonly '} class="form-control" maxlength="${field.renderer._config._tree.attrib.get("maxlength")}" id="${field.id}" name="${field.name}" rows="${field.renderer.rows}">${field.get_value()}</textarea>
  % if field.renderer._config._tree.attrib.get("maxlength"):
    <div id="${field.id}_feedback" class="pull-right text-muted small"></div>
    <script>
      $('#${field.id}').keyup(function() {
        calcRemainingChars("${field.id}", "${_('characters remaining')}");
      });
      calcRemainingChars("${field.id}", "${_('characters remaining')}");
    </script>
  % endif
% endif
