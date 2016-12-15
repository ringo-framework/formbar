% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}">
  </div>
% else:
  <div id="file-container">
    <div id="file-upload">
      <input class="form-control" id="${field.id}" name="${field.name}" type="file" value="" onchange="loadFile(event)"/>
    </div>
    <div id="file-preview">
      <p id="file-preview-placeholder">${_("Image Preview")}</p>
      <img id="file-preview-image" class="img-responsive"/>
    </div>
  </div>
  <script>
    var loadFile = function(event) {
      var reader = new FileReader();
      reader.onload = function(){
        var output = document.getElementById('file-preview-image');
        var placeholder = document.getElementById('file-preview-placeholder');
        // Only update preview if it is an image
        if ( reader.result.indexOf("data:image") == 0 ) {
          output.src = reader.result;
          $(placeholder).hide();
        } else {
          output.src = "";
          $(placeholder).show();
        }
      };
      reader.readAsDataURL(event.target.files[0]);
    };
  </script>
% endif
