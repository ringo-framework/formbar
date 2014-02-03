.. _examples:

Examples
********

More examples with screenshots are planned. Sorry for only giving one example.

Example 1
=========
Here we go::

  <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
  <configuration>
    <source>
      <entity id="e1" name="string" label="String field" type="string" readonly="true"/>
      <entity id="e2" name="integer" label="Integer field" type="integer" required="true">
        <rule expr="$integer ge 16" msg="Integer must be greater than 15" mode="post"/>
      </entity>
      <entity id="e3" name="float" label="Float field" type="float">
        <rule expr="$float lt 100" msg="Float must be lower than 100" mode="post"/>
        <help>This is is a very long helptext which should span over
        multiple rows. Further the will check if there are further html
        tags allowed.</help>
      </entity>
      <entity id="e4" name="date" label="Date field" type="date" autocomplete="off" number="1">
        <renderer type="datepicker"/>
        <help>This is my helptext</help>
      </entity>
      <entity id="e5" name="select" label="Select field" type="string">
        <help>This is my helptext</help>
        <renderer type="dropdown"/>
        <options>
          <option value="1">Option 1</option>
          <option value="2">Option 2</option>
          <option value="3">Option 3</option>
          <option value="4">Option 4</option>
        </options>
      </entity>
      <entity id="e6" name="optional" label="Optional field">
        <help>This field is only shown if the Dropdown has selected option 4</help>
      </entity>
    </source>
    <form id="example1" css="testcss" autocomplete="off" method="POST" action="" enctype="multipart/form-data">
      <snippet ref="s1"/>
    </form>
    <snippet id="s1">
      <row>
        <col><field ref="e3"/></col>
        <col><field ref="e4"/></col>
      </row>
      <row>
        <col><field ref="e5"/></col>
      </row>
      <snippet ref="s2"/>
    </snippet>
    <snippet id="s2">
      <row>
        <col><field ref="e1"/></col>
        <col><field ref="e2"/></col>
      </row>
      <row>
        <if type="readonly" expr="$select == 4">
          <col><field ref="e6"/></col>
        </if>
      </row>
    </snippet>
  </configuration>
