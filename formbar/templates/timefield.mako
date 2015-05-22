% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    ${field.get_value("")}
  </div>
% else:
  <input class="form-control" id="${field.id}" type="text" name="${field.name}" value="${field.get_value()}" placeholder="${field.placeholder or 'HH:MM:SS'}"/>
% endif
<script>
$('#${field.id}').keyup(function() {
    /* TODO: Check wo to improve to prevent the user to insert only
    allowed chars. Now the char can be entered but it gets replaced
    imediately if it does not match the allowed char. (None) <2013-08-25
    21:11> */
    this.value = this.value.replace(/[^0-9:]/g, '');
});

</script>
