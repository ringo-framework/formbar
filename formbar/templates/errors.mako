% for error in field.get_errors():
  <div class="help-block">
    <span class="glyphicon glyphicon-exclamation-sign"></span>
    ${_(error)}
  </div>
% endfor
% for warn in field.get_warnings():
  <div class="help-block">
    <span class="text-warning">
    <span class="glyphicon glyphicon-warning-sign"></span>
    ${_(warn)}
    </span>
  </div>
% endfor
