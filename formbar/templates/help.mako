% if field.help is not None and field.help_display == "text":
<p class="text-help">
   <span class="glyphicon glyphicon-info-sign"></span>
   ${_(field.help) | n}
</p>
% endif
