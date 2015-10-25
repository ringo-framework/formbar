<%
value = field.get_value() or []
selected = [str(id) for id in value if id]
inputvalue = []
for option in options:
  if str(option[1]) in selected:
    inputvalue.append(str(option[0]))
%>
% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
    ${field.get_value(expand=True) or "&nbsp;"}
  </div>
% else:
  <select class="hidden" name="${field.name}" size="5" multiple>
    % for option in options:
      <option value="" selected="selected"></option>
      ## Depending if the options has passed the configured filter the
      ## option will be visible or hidden
      % if option[2]:
        % if str(option[1]) in selected:
          <option value="${option[1]}" selected="selected">${option[0]}</option>
        % else:
          <option value="${option[1]}">${option[0]}</option>
        % endif
      % elif not field.renderer.remove_filtered == "true":
        <option value="${option[1]}" class="hidden">${option[0]}</option>
      % endif
    % endfor
  </select>
  <input class="form-control textoption" type="text" id="${field.id}" name="_${field.name}" value="${', '.join(inputvalue)}" ${field.autofocus and 'autofocus'}/>
% endif
<script>

var ${field.id}_tags = ${'[%s]' % ", ".join('"%s"' % option[0] for option in options) |n};

function split( val ) {
  return val.split( /,\s*/ );
}
function extractLast( term ) {
  return split( term ).pop();
}

$( "#${field.id}" )
  // don't navigate away from the field on tab when selecting an item
  .bind( "keydown", function( event ) {
    if ( event.keyCode === $.ui.keyCode.TAB &&
        $( this ).autocomplete( "instance" ).menu.active ) {
      event.preventDefault();
    }
  })
  .autocomplete({
    minLength: 0,
    source: function( request, response ) {
      // delegate back to autocomplete, but extract the last term
      response( $.ui.autocomplete.filter(
        ${field.id}_tags, extractLast( request.term ) ) );
    },
    focus: function() {
      // prevent value inserted on focus
      return false;
    },
    select: function( event, ui ) {
      var terms = split( this.value );
      // remove the current input
      terms.pop();
      // add the selected item
      terms.push( ui.item.value );
      this.value = terms.join( ", " );
      return false;
    }
  });


$('div.formbar-form input.textoption').focusout(function() {
  var options = split($(this).val());
  console.log(options);
  $('select[name="${field.name}"] > option').each(function() {
    if ($(this.value) != "") {
      $(this).attr('selected', false);
    }
  });
  $('select[name="${field.name}"] > option').each(function() {
    if ($.inArray(this.text, options) > -1) {
      console.log(this.text);
      $(this).attr('selected', true);
    }
  });
});
</script>
