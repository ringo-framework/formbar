## Render pages
% if len(form._config.get_elements('page')) > 0:
  ## Render tabs
  <div class="tabbable tabs-right">
    <ul class="nav nav-tabs">
    % for num, page in enumerate(form._config.get_elements('page')):
      <li class="${num==0 and 'active'}"><a href="#${page.attrib.get('id')}" data-toggle="tab">${page.attrib.get('label')}</a></li>
    % endfor
    </ul>
    ## Render tabs-content 
    <div class="tab-content">
    % for num, page in enumerate(form._config.get_elements('page')):
      <div class="tab-pane ${num==0 and 'active'}" id="${page.attrib.get('id')}">
        ${self.render_recursive(page)}
      </div>
    % endfor
    </div>
  </div>
% else:
    ${self.render_recursive(form._config._tree)}
% endif

<%def name="render_recursive(elem)">
  % for child in elem:
    % if len(child) > 0:
      % if child.tag == "row":
        <div class="row-fluid"><tr>
      % elif child.tag == "col":
        <% width = child.attrib.get('width', (12/len(elem))) %>
        <div class="span${width}">
      % elif child.tag == "fieldset":
        <fieldset>
        <legend>${child.attrib.get('label')}</legend>
      % endif
      ${self.render_recursive(child)}
      % if child.tag == "fieldset":
        </fieldset>
      % elif child.tag == "col":
        </div>
      % elif child.tag == "row":
        </div>
      % endif
    % else:
      % if child.tag == "field":

        <% field = form.get_field(form._config._id2name[child.attrib.get('ref')]) %>
        <% fieldconfig = form._config.get_field(field.key) %>
        <label for="${field.name}">
          ${field.label()}
          % if field.is_required():
            <a href="#" data-toggle="tooltip" class="formbar-tooltip" data-original-title="Required field"><i class="icon-asterisk"></i></a>
          % endif
        </label>
        % if field.is_readonly():
          <div class="readonlyfield">
            ${field.readonly().render() or "&nbsp;"}
          </div>
        % else:
          ${field.render()}
        % endif
        ## Errors
        % if len(field.errors) > 0:
          % for error in field.errors:
            <i class="icon-exclamation-sign"></i>
            <div class="text-error">${error}</div>
          % endfor
        % endif
        ## Helptexts
        % if fieldconfig.help is not None:
        <div class="text-help">
          <i class="icon-info-sign"></i>
          ${fieldconfig.help}
        </div>
        % endif
      % elif child.tag == "snippet":
        <% ref = child.attrib.get('ref') %>
        % if ref:
          <% child = form._config._parent.get_element('snippet', ref) %>
        % endif
        ${self.render_recursive(child)}
      % endif
    % endif
  % endfor
</%def>
<script>
  $('.formbar-tooltip').tooltip();
</script>
