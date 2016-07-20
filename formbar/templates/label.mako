<label class="control-label ${field.renderer.label_background} ${field.renderer.label_position} ${field.renderer.render_type}" for="${field.name}">
  % if field.renderer.elements_indent:
    <span class="indent ${field.renderer.indent_style} ${field.renderer.indent_border} ${field.renderer.indent_width}">
      % if field.renderer.indent_style == "indent-symbol":
        <i style="font-size:130%" class="fa fa-caret-right"></i>
      % elif field.renderer.indent_style == "indent-number":
        ${field.number}
      % endif
    </span>
  % endif
  <span class="label-content  ${field.renderer.elements_indent and field.renderer.indent_width}">
  % if field.number and field.renderer.indent_style != "indent-number":
    <sup>[${field.number}]</sup>
  % endif
    % if field.label:
        ${_(field.label)}
    % endif
    % if field.is_required:
      <span data-toggle="tooltip" data-original-title="${_('Required field')}" class="formbar-tooltip glyphicon glyphicon-asterisk hidden-print"></span>
    % endif
    % if field.help is not None and field.help_display == "tooltip":
      <span data-toggle="tooltip" data-original-title="${_(field.help)}" class="formbar-tooltip glyphicon glyphicon-info-sign hidden-print"></span>
    % endif
    % if field.number and field.renderer.number == "right" and field.renderer.indent_style != "indent-number":
      <sup>[${field.number}]</sup>
    % endif
  </span>
</label>
