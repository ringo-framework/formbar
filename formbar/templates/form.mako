## Render pages
% if len(form._config.get_pages()) > 0:
  ## Render tabs
  <div class="tabbable tabs-right">
    <ul class="nav nav-tabs">
    % for num, page in enumerate(form._config.get_pages()):
      <li class="${num==form.current_page-1 and 'active'}"><a href="#${page.attrib.get('id')}" data-toggle="tab" formbar-item="${form.change_page_callback.get('item')}" formbar-itemid="${form.change_page_callback.get('itemid')}">${page.attrib.get('label')}</a></li>
    % endfor
    </ul>
    ## Render tabs-content 
    <div class="tab-content">
    % for num, page in enumerate(form._config.get_pages()):
      <div class="tab-pane ${num==form.current_page-1 and 'active'}" id="${page.attrib.get('id')}">
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
        <div class="row-fluid">
      % elif child.tag == "col":
        <% width = child.attrib.get('width', (12/len(elem))) %>
        <div class="span${width}">
      % elif child.tag == "fieldset":
        <fieldset>
        <legend>${child.attrib.get('label')}</legend>
      ## Table rendering
      % elif child.tag == "table":
        <table class="table table-condensed table-bordered table-striped">
      % elif child.tag == "tr":
        <tr>
      % elif child.tag == "th":
        <th>
      % elif child.tag == "td":
        <td class="${child.attrib.get('class', '')}" width="${child.attrib.get('width', '')}">
      % endif
      ${self.render_recursive(child)}
      % if child.tag == "fieldset":
        </fieldset>
      % elif child.tag == "col":
        </div>
      % elif child.tag == "row":
        </div>

      ## Table rendering
      % elif child.tag == "table":
        </table>
      % elif child.tag == "tr":
        </tr>
      % elif child.tag == "th":
        </th>
      % elif child.tag == "td":
        </td>
      % endif
    % else:
      % if child.tag == "field":
        <% field = form.get_field(form._config._id2name[child.attrib.get('ref')]) %>
        ${field.render()}
      % elif child.tag == "snippet":
        <% ref = child.attrib.get('ref') %>
        % if ref:
          <% child = form._config._parent.get_element('snippet', ref) %>
        % endif
        ${self.render_recursive(child)}
      ## Table rendering
      % elif child.tag == "th":
        <th>${child.text}</th>
      % elif child.tag == "td":
        <td class="${child.attrib.get('class', '')}"
        width="${child.attrib.get('width', '')}">${child.text or ""}</td>
      % endif
    % endif
  % endfor
</%def>

<%def name="render_table(elem)">
</%def>
