## Render pages
<div class="row">
% if render_outline and len(form._config.get_pages()) > 0:
  <div class="col-sm-3">
    <div>
      <div class="panel panel-default formbar-outline">
        <!-- Default panel contents -->
        <div class="panel-heading">${_('Outline')}</div>
        <!-- List group -->
        <ul class="list-group">
          ${self.render_recursive_outline(form, form._config._tree)}
          ##% for num, page in enumerate(form._config.get_pages()):
          ##  <a href="#${page.attrib.get('id')}" class="list-group-item" formbar-item="${form.change_page_callback.get('item')}" formbar-itemid="${form.change_page_callback.get('itemid')}">${page.attrib.get('label')}
          ##  <span class="label label-danger pull-right">${len(form.get_errors(page)) or ""}</span>
          ##  <span class="label label-warning pull-right">${len(form.get_warnings(page)) or ""}</span>
          ##  </a>
          ##% endfor
        </ul>
      </div>
    </div>
  </div>
  <div class="col-sm-9">
  % for num, page in enumerate(form._config.get_pages()):
    <div class="formbar-page ${num==form.current_page-1 and 'active'}" id="formbar-page-${num+1}">
      <h2>${page.attrib.get('label')}</h2>
      ${self.render_recursive(page)}
    </div>
  % endfor
  </div>
% else:
  <div class="col-sm-12">
    ${self.render_recursive(form._config._tree)}
  </div>
% endif
</div>

<%def name="render_recursive_outline(form, element)">
  % for child in element:
    % if child.tag == "snippet":
      <% ref = child.attrib.get('ref') %>
      % if ref:
        <% child = form._config._parent.get_element('snippet', ref) %>
      % endif
    % elif child.tag == "page":
      ${self.render_outline_element(form, child)}
    % elif child.tag == "if" and child[0].tag == "page":
      <div class="formbar-conditional ${child.attrib.get('type')}" expr="${child.attrib.get('expr')}">
    % endif
    ${self.render_recursive_outline(form, child)}
    % if child.tag == "if" and child[0].tag == "page":
      </div>
    % endif
  % endfor
</%def>

<%def name="render_outline_element(form, page)">
  <a href="#${page.attrib.get('id')}" class="list-group-item" formbar-item="${form.change_page_callback.get('item')}" formbar-itemid="${form.change_page_callback.get('itemid')}">${page.attrib.get('label')}
  <span class="label label-danger pull-right">${len(form.get_errors(page)) or ""}</span>
  <span class="label label-warning pull-right">${len(form.get_warnings(page)) or ""}</span>
  </a>
</%def>

<%def name="render_recursive(elem)">
  % for child in elem:
    % if len(child) > 0:
      % if child.tag == "page" and not render_outline:
        <h3>${child.attrib.get("label")}</h3>
      % elif child.tag == "row":
        <div class="row row-fluid">
      % elif child.tag == "col":
        <% width = child.attrib.get('width', (12/len(elem))) %>
        <div class="col-md-${width} span${width}">
      % elif child.tag == "fieldset":
        <fieldset>
        <legend>${child.attrib.get('label')}</legend>
      ## Table rendering
      % elif child.tag == "table":
        <table class="table table-condensed table-bordered table-striped">
      % elif child.tag == "tr":
        <tr class="${child.attrib.get('class', '')}">
      % elif child.tag == "th":
        <th colspan="${child.attrib.get('colspan', '')}" class="${child.attrib.get('class', '')}" rowspan="${child.attrib.get('rowspan', '')}" width="${child.attrib.get('width', '')}">
      % elif child.tag == "td":
        <td colspan="${child.attrib.get('colspan', '')}" class="${child.attrib.get('class', '')}" rowspan="${child.attrib.get('rowspan', '')}" width="${child.attrib.get('width', '')}">
      ## Conditionals
      % elif child.tag == "if":
        <div class="formbar-conditional ${child.attrib.get('type')}" expr="${child.attrib.get('expr')}">
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
      % elif child.tag == "if":
        </div>
      % endif
    % else:
      % if child.tag == "field":
        ${form.get_field(form._config._id2name[child.attrib.get('ref')]).render()}
      % elif child.tag == "snippet":
        <% ref = child.attrib.get('ref') %>
        % if ref:
          <% child = form._config._parent.get_element('snippet', ref) %>
        % endif
        ${self.render_recursive(child)}
      ## Others
      % elif child.tag == "text":
        <%
          textclasses = []
          if child.attrib.get('bg'):
            textclasses.append("bg-%s" % child.attrib.get('bg'))
            textclasses.append("text-generic")
          if child.attrib.get('color'):
            textclasses.append("text-%s" % child.attrib.get('color'))
        %>
        <p class="${' '.join(textclasses)}">
          % if child.attrib.get('em'):
            % for em in child.attrib.get('em').split(" "):
              <${em}>
            % endfor
              ${child.text}
            % for em in child.attrib.get('em').split(" "):
              </${em}>
            % endfor
          % else:
            ${child.text}
          % endif
        </p>
      ## Table rendering
      % elif child.tag == "th":
        <th colspan="${child.attrib.get('colspan', '')}" class="${child.attrib.get('class', '')}" rowspan="${child.attrib.get('rowspan', '')}" width="${child.attrib.get('width', '')}">${child.text}</th>
      % elif child.tag == "td":
        <td colspan="${child.attrib.get('colspan', '')}" class="${child.attrib.get('class', '')}" rowspan="${child.attrib.get('rowspan', '')}" width="${child.attrib.get('width', '')}">${child.text or ""}</td>
      % endif
    % endif
  % endfor
</%def>
