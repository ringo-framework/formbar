## Render pages
<div class="row">
% if render_outline and len(form.pages) > 0:
  <div class="col-sm-3 hidden-print">
    <div>
      <div class="panel panel-default formbar-outline">
        <!-- Default panel contents -->
        <div class="panel-heading">${_('Outline')}</div>
        <!-- List group -->
        <ul class="list-group">
          ${self.render_recursive_outline(form, form._config._tree)}
          ##% for num, page in enumerate(form.pages):
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
  % for num, page in enumerate(form.pages):
    <div class="formbar-page ${num==form.current_page-1 and 'active'}" id="formbar-page-${num+1}">
      <h1 class="page">${_(page.attrib.get('label'))}</h1>
      ## Render errors and warnings
      % for warn in form.warnings:
        <div class="alert alert-warning" role="warning"><i class="glyphicon glyphicon-exclamation-sign"></i> ${warn}</div>
      % endfor
      % for err in form.errors:
        <div class="alert alert-danger" role="alert"><i class="glyphicon glyphicon-exclamation-sign"></i> ${err}</div>
      % endfor
      ${self.render_recursive(page)}
    </div>
  % endfor
  </div>
% else:
  <div class="col-sm-12">
      ## Render errors and warnings
      % for warn in form.warnings:
        <div class="alert alert-warning" role="warning"><i class="glyphicon glyphicon-exclamation-sign"></i> ${warn}</div>
      % endfor
      % for err in form.errors:
        <div class="alert alert-danger" role="alert"><i class="glyphicon glyphicon-exclamation-sign"></i> ${err}</div>
      % endfor
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
    % elif child.tag == "if" and child[0].tag == "page" and child.attrib.get("static") != "true":
      <div id="${id(child)}" class="formbar-conditional ${child.attrib.get('type')}" reset-value="${child.attrib.get('reset-value', 'false')}" expr="${child.attrib.get('expr')}">
    % endif
    % if child.attrib.get("static") != "true" or Rule(child.attrib.get("expr")).evaluate(form.merged_data):
      ${self.render_recursive_outline(form, child)}
    % endif:
    % if child.tag == "if" and child[0].tag == "page" and child.attrib.get("static") != "true":
      </div>
    % endif
  % endfor
</%def>

<%def name="render_outline_element(form, page)">
  <a href="#${page.attrib.get('id')}" class="list-group-item ${(int(page.attrib.get('id').strip("p"))==form.current_page) and 'selected'}" formbar-lastpage="${str(form.last_page==int(page.attrib.get('id').strip("p"))).lower()}" formbar-baseurl="${form._url_prefix}" formbar-item="${form.change_page_callback.get('item')}" formbar-itemid="${form.change_page_callback.get('itemid')}">${_(page.attrib.get('label'))}
  <span class="label label-danger pull-right">${len(form.get_errors(page)) or ""}</span>
  <span class="label label-warning pull-right">${len(form.get_warnings(page)) or ""}</span>
  </a>
</%def>

<%def name="render_recursive(elem, mode='', active=True)">
  % for child in elem:
    <%
      if mode == 'hide':
        continue
      is_active = active
    %>
    % if len(child) > 0:
      % if child.tag == "page" and not render_outline:
        <h1 class="page">${_(child.attrib.get("label"))}</h1>
      % elif child.tag == "section":
        <h2 class="section">${_(child.attrib.get('label'))}</h2>
      % elif child.tag == "subsection":
        <h3 class="section">${_(child.attrib.get('label'))}</h3>
      % elif child.tag == "subsubsection":
        <h4 class="section">${_(child.attrib.get('label'))}</h4>
      % elif child.tag == "row":
        <div class="row row-fluid">
      % elif child.tag == "col":
        <% width = child.attrib.get('width', (12/len(elem))) %>
        <div class="col-md-${width} span${width}">
      % elif child.tag == "fieldset":
        <fieldset>
        <legend>${_(child.attrib.get('label'))}</legend>
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
      % elif child.tag == "if" and child.attrib.get("static") != "true":
        <% 
        is_active = Rule(child.attrib.get("expr")).evaluate(form.merged_data) 
        is_readonly = child.attrib.get('type') == 'readonly'
        if is_active:
          css_class = "active"
        else:
          # If the conditional evaluates to False (inactive) and the field is
          # not a readonly field the content of the conditional must be
          # hidden on initial load of the form.
          css_class = "inactive {} {}".format(child.attrib.get('type'), '' if is_readonly else 'hidden')
        %>
        <div id="${id(child)}" type="${child.attrib.get('type')}" class="formbar-conditional ${css_class}" reset-value="${child.attrib.get('reset-value', 'false')}" expr="${child.attrib.get('expr')}">
      % elif child.tag == "html":
        ${ElementTree.tostring(child) | n}
      % endif
      % if child.attrib.get("static") != "true" or Rule(child.attrib.get("expr")).evaluate(form.merged_data):
        ${self.render_recursive(child, mode, active=is_active)}
      % else:
        ${self.render_recursive(child, child.attrib.get('type', 'hide'), active=is_active)}
      % endif
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
      % elif child.tag == "if" and child.attrib.get("static") != "true":
        </div>
      % endif
    % else:
      % if child.tag == "field":
        <%
          field = form.get_field(form._config._id2name[child.attrib.get('ref')])
          if mode == "readonly":
            field.readonly = True
        %>
        ${field.render(active) | n}
      % elif child.tag == "snippet":
        <% ref = child.attrib.get('ref') %>
        % if ref:
          <% child = form._config._parent.get_element('snippet', ref) %>
        % endif
        ${self.render_recursive(child, active=is_active)}
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
              ${_(child.text)}
            % for em in child.attrib.get('em').split(" "):
              </${em}>
            % endfor
          % else:
            ${_(child.text)}
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
