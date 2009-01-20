#!/usr/bin/python
#
# Copyright (C) 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Converts Python data into data for Google Visualization API clients.

This library can be used to create a google.visualization.DataTable usable by
visualizations built on the Google Visualization API. Output formats are raw
JSON, JSON response, and JavaScript.

See http://code.google.com/apis/visualization/ for documentation on the
Google Visualization API.
"""

__author__ = "Amit Weinstein, Misha Seltzer"

import datetime
import logging

class DataTableException(Exception):
  """The general exception object thrown by DataTable."""
  pass


class DataTable(object):

  """Wraps the data to convert to a Google Visualization API DataTable.

  Create this object, populate it with data, then call one of the ToJS...
  methods to return a string representation of the data in the format described.

  You can clear all data from the object to reuse it, but you cannot clear
  individual cells, rows, or columns. You also cannot modify the table schema
  specified in the class constructor.

  You can add new data one or more rows at a time. All data added to an
  instantiated DataTable must conform to the schema passed in to __init__().

  You can reorder the columns in the output table, and also specify row sorting
  order by column. The default column order is according to the original
  table_description parameter. Default row sort order is ascending, by column
  1 values. For a dictionary, we sort the keys for order.

  The data and the table_description are closely tied, as described here:

  The table schema is defined in the class constructor's table_description
  parameter. The user defines each column using a tuple of
  (id[, type, [label]]). The default value for type is string, and label
  is the same as ID if not specified.

  table_description is a dictionary or list, containing one or more column
  descriptor tuples, nested dictionaries, and lists. Each dictionary key, list
  element, or dictionary element must eventually be defined as
  a column description tuple. Here's an example of a dictionary where the key
  is a tuple, and the value is a list of two tuples:
    {('a', 'number'): [('b', 'number'), ('c', 'string')]}

  This flexibility in data entry enables you to build and manipulate your data
  in a Python structure that makes sense for your program.

  Add data to the table using the same nested design as the table's
  table_description, replacing column descriptor tuples with cell data, and
  each row is an element in the top level collection. This will be a bit
  clearer after you look at the following examples showing the
  table_description, matching data, and the resulting table:

  Columns as list of tuples [col1, col2, col3]
    table_description: [('a', 'number'), ('b', 'string')]
    AppendData( [[1, 'z'], [2, 'w'], [4, 'o'], [5, 'k']] )
    Table:
    a  b   <--- these are column ids/labels
    1  z
    2  w
    4  o
    5  k

  Dictionary of columns, where key is a column, and value is a list of
  columns  {col1: [col2, col3]}
    table_description: {('a', 'number'): [('b', 'number'), ('c', 'string')]}
    AppendData( data: {1: [2, 'z'], 3: [4, 'w']}
    Table:
    a  b  c
    1  2  z
    3  4  w

  Dictionary where key is a column, and the value is itself a dictionary of
  columns {col1: {col2, col3}}
    table_description: {('a', 'number'): {'b': 'number', 'c': 'string'}}
    AppendData( data: {1: {'b': 2, 'c': 'z'}, 3: {'b': 4, 'c': 'w'}}
    Table:
    a  b  c
    1  2  z
    3  4  w
  """

  def __init__(self, table_description, data=None):
    """Initialize the data table from a table schema and (optionally) data.

    See the class documentation for more information on table schema and data
    values.

    Args:
      table_description: A table schema, following one of the formats described
                         in TableDescriptionParser(). Schemas describe the
                         column names, data types, and labels. See
                         TableDescriptionParser() for acceptable formats.
      data: Optional. If given, fills the table with the given data. The data
            structure must be consistent with schema in table_description. See
            the class documentation for more information on acceptable data. You
            can add data later by calling AppendData().

    Raises:
      DataTableException: Raised if the data and the description did not match,
                          or did not use the supported formats.
    """
    self.__columns = self.TableDescriptionParser(table_description)
    self.__data = []
    if data:
      self.LoadData(data)

  @staticmethod
  def SingleValueToJS(value, value_type):
    """Translates a single value and type into a JS value.

    Internal helper method.

    Args:
      value: The value which should be converted
      value_type: One of "string", "number", "boolean", "date", "datetime" or
                  "timeofday".

    Returns:
      The proper JS format (as string) of the given value according to the
      given value_type. For None, we simply return "null".
      If a tuple is given, it should be of the form (value, formatted value)
      where the formatted value is a string. In such a case, we return
      the tuple of (JS value as string, formatted value).
      The real type of the given value is not strictly checked. For example,
      any type can be used for string - as we simply take its str( ) and for
      boolean value we just check "if value".
      Examples:
        SingleValueToJS(False, "boolean") returns "false"
        SingleValueToJS((5, "5$"), "number") returns ("5", "'5$'")

    Raises:
      DataTableException: The value and type did not match in a not-recoverable
                          way, for example given value 'abc' for type 'number'.
    """
    if isinstance(value, tuple):
      # In case of a tuple, we run the same function on the value itself and
      # add the formatted value.
      if len(value) != 2:
        raise DataTableException("Wrong format for value and formatting - %s." %
                                 str(value))
      if not isinstance(value[1], str):
        raise DataTableException("Formatted value is not string, given %s." %
                                 type(value[1]))
      js_value = DataTable.SingleValueToJS(value[0], value_type)
      if js_value == "null":
        raise DataTableException("An empty cell can not have formatting.")
      # Here we use python built-in escaping mechanism for string using repr.
      return (js_value, repr(str(value[1])))

    # The standard case - no formatting.
    t_value = type(value)
    if value is None:
      return "null"
    if value_type == "boolean":
      if value:
        return "true"
      return "false"

    elif value_type == "number":
      if isinstance(value, (int, long, float)):
        return str(value)
      else:
        return repr(value)
        logging.debug('Problem with ' + value)
      raise DataTableException("Wrong type %s when expected number" % t_value)

    elif value_type == "string":
      if isinstance(value, tuple):
        raise DataTableException("Tuple is not allowed as string value.")
      try:
        return repr(str(value))
      except:
        return repr(unicode(value))

    elif value_type == "date":
      if not isinstance(value, (datetime.date, datetime.datetime)):
        raise DataTableException("Wrong type %s when expected date" % t_value)
        # We need to shift the month by 1 to match JS Date format
      return "new Date(%d,%d,%d)" % (value.year, value.month - 1, value.day)

    elif value_type == "timeofday":
      if not isinstance(value, (datetime.time, datetime.datetime)):
        raise DataTableException("Wrong type %s when expected time" % t_value)
      return "[%d,%d,%d]" % (value.hour, value.minute, value.second)

    elif value_type == "datetime":
      if not isinstance(value, datetime.datetime):
        raise DataTableException("Wrong type %s when expected datetime" %
                                 t_value)
      return "new Date(%d,%d,%d,%d,%d,%d)" % (value.year,
                                              value.month - 1,  # To match JS
                                              value.day,
                                              value.hour,
                                              value.minute,
                                              value.second)
    # If we got here, it means the given value_type was not one of the
    # supported types.
    raise DataTableException("Unsupported type %s" % value_type)

  @staticmethod
  def ColumnTypeParser(description):
    """Parses a single column description. Internal helper method.

    Args:
      description: a column description in the possible formats:
       'id'
       ('id',)
       ('id', 'type')
       ('id', 'type', 'label')
    Returns:
      Dictionary with the following keys: id, label and type where:
        - If label not given, it equals the id.
        - If type not given, string is used by default.

    Raises:
      DataTableException: The column description did not match the RE.
    """
    if not description:
      raise DataTableException("Description error: empty description given")

    if not isinstance(description, (str, tuple)):
      raise DataTableException("Description error: expected either string or "
                               "tuple, got %s." % type(description))

    if isinstance(description, str):
      description = (description,)

    # According to the tuple's length, we fill the keys
    # We verify everything is of type string
    for elem in description:
      if not isinstance(elem, str):
        raise DataTableException(("Description error: expected tuple of "
                                  "strings, current element of type %s." %
                                  type(elem)))
    desc_dict = {"id": description[0],
                 "label": description[0],
                 "type": "string"}
    if len(description) > 1:
      desc_dict["type"] = description[1].lower()
      if len(description) > 2:
        desc_dict["label"] = description[2]
        if len(description) > 3:
          raise DataTableException("Description error: tuple of length > 3")
    return desc_dict

  @staticmethod
  def TableDescriptionParser(table_description, depth=0):
    """Parses the table_description object for internal use.

    Parses the user-submitted table description into an internal format used
    by the Python DataTable class. Returns the flat list of parsed columns.

    Args:
      table_description: A description of the table which should comply
                         with one of the formats described below.
      depth: Optional. The depth of the first level in the current description.
             Used by recursive calls to this function.

    Returns:
      List of columns, where each column represented by a dictionary with the
      keys: id, label, type, depth, container which means the following:
      - id: the id of he column
      - name: The name of the column
      - type: The datatype of the elements in this column. Allowed types are
              described in ColumnTypeParser().
      - depth: The depth of this column in the table description
      - container: 'dict', 'iter' or 'scalar' for parsing the format easily.
      The returned description is flattened regardless of how it was given.

    Raises:
      DataTableException: Error in a column description or in the description
                          structure.

    Examples:
      A column description can be of the following forms:
       'id'
       ('id',)
       ('id', 'type')
       ('id', 'type', 'label')
       or as a dictionary:
       'id': 'type'
       'id': ('type',)
       'id': ('type', 'label')
      If the type is not specified, we treat it as string.
      If no specific label is given, the label is simply the id.

      input: [('a', 'date'), ('b', 'timeofday')]
      output: [{'id': 'a', 'label': 'a', 'type': 'date',
                'depth': 0, 'container': 'iter'},
               {'id': 'b', 'label': 'b', 'type': 'timeofday',
               'depth': 0, 'container': 'iter'}]

      input: {'a': [('b', 'number'), ('c', 'string', 'column c')]}
      output: [{'id': 'a', 'label': 'a', 'type': 'string',
                'depth': 0, 'container': 'dict'},
               {'id': 'b', 'label': 'b', 'type': 'number',
                'depth': 1, 'container': 'iter'},
               {'id': 'c', 'label': 'column c', 'type': 'string',
                'depth': 1, 'container': 'iter'}]

      input:  {('a', 'number', 'column a'): { 'b': 'number', 'c': 'string'}}
      output: [{'id': 'a', 'label': 'column a', 'type': 'number',
                'depth': 0, 'container': 'dict'},
               {'id': 'b', 'label': 'b', 'type': 'number',
                'depth': 1, 'container': 'dict'},
               {'id': 'c', 'label': 'c', 'type': 'string',
                'depth': 1, 'container': 'dict'}]

      input: { ('w', 'string', 'word'): ('c', 'number', 'count') }
      output: [{'id': 'w', 'label': 'word', 'type': 'string',
                'depth': 0, 'container': 'dict'},
               {'id': 'c', 'label': 'count', 'type': 'number',
                'depth': 1, 'container': 'scalar'}]
    """
    # For the recursion step, we check for a scalar object (string or tuple)
    if isinstance(table_description, (str, tuple)):
      parsed_col = DataTable.ColumnTypeParser(table_description)
      parsed_col["depth"] = depth
      parsed_col["container"] = "scalar"
      return [parsed_col]

    # Since it is not scalar, table_description must be iterable.
    if not hasattr(table_description, "__iter__"):
      raise DataTableException("Expected an iterable object, got %s" %
                               type(table_description))
    if not isinstance(table_description, dict):
      # We expects a non-dictionary iterable item.
      columns = []
      for desc in table_description:
        parsed_col = DataTable.ColumnTypeParser(desc)
        parsed_col["depth"] = depth
        parsed_col["container"] = "iter"
        columns.append(parsed_col)
      if not columns:
        raise DataTableException("Description iterable objects should not"
                                 " be empty.")
      return columns
    # The other case is a dictionary
    if not table_description:
      raise DataTableException("Empty dictionaries are not allowed inside"
                               " description")

    # The number of keys in the dictionary separates between the two cases of
    # more levels below or this is the most inner dictionary.
    if len(table_description) != 1:
      # This is the most inner dictionary. Parsing types.
      columns = []
      # We sort the items, equivalent to sort the keys since they are unique
      for key, value in sorted(table_description.items()):
        # We parse the column type as (key, type) or (key, type, label) using
        # ColumnTypeParser.
        if isinstance(value, tuple):
          parsed_col = DataTable.ColumnTypeParser((key,) + value)
        else:
          parsed_col = DataTable.ColumnTypeParser((key, value))
        parsed_col["depth"] = depth
        parsed_col["container"] = "dict"
        columns.append(parsed_col)
      return columns
    # This is an outer dictionary, must have at most one key.
    parsed_col = DataTable.ColumnTypeParser(table_description.keys()[0])
    parsed_col["depth"] = depth
    parsed_col["container"] = "dict"
    return ([parsed_col] +
            DataTable.TableDescriptionParser(table_description.values()[0],
                                             depth=depth + 1))

  @property
  def columns(self):
    """Returns the parsed table description."""
    return self.__columns

  def NumberOfRows(self):
    """Returns the number of rows in the current data stored in the table."""
    return len(self.__data)

  def LoadData(self, data):
    """Loads new data to the data table, clearing existing data."""
    self.__data = []
    self.AppendData(data)

  def AppendData(self, data):
    """Appends new data to the table.

    Data is appended in rows. Data must comply with
    the table schema passed in to __init__(). See SingleValueToJS() for a list
    of acceptable data types. See the class documentation for more information
    and examples of schema and data values.

    Args:
      data: The row to add to the table. The data must conform to the table
            description format.

    Raises:
      DataTableException: The data structure does not match the description.
    """
    # If the maximal depth is 0, we simply iterate over the data table
    # lines and insert them using InnerLoadData. Otherwise, we simply
    # let the InnerLoadData handle all the levels.
    if not self.__columns[-1]["depth"]:
      for line in data:
        self._InnerAppendData({}, line, 0)
    else:
      self._InnerAppendData({}, data, 0)

  def _InnerAppendData(self, prev_col_values, data, col_index):
    """Inner function to assist LoadData."""
    # We first check that col_index has not exceeded the columns size
    if col_index >= len(self.__columns):
      raise DataTableException("The data does not match description, too deep")

    # Dealing with the scalar case, the data is the last value.
    if self.__columns[col_index]["container"] == "scalar":
      prev_col_values[self.__columns[col_index]["id"]] = data
      self.__data.append(prev_col_values)
      return

    if self.__columns[col_index]["container"] == "iter":
      if not hasattr(data, "__iter__") or isinstance(data, dict):
        raise DataTableException("Expected iterable object, got %s" %
                                 type(data))
      # We only need to insert the rest of the columns
      # If there are less items than expected, we only add what there is.
      for value in data:
        if col_index >= len(self.__columns):
          raise DataTableException("Too many elements given in data")
        prev_col_values[self.__columns[col_index]["id"]] = value
        col_index += 1
      self.__data.append(prev_col_values)
      return

    # We know the current level is a dictionary, we verify the type.
    if not isinstance(data, dict):
      raise DataTableException("Expected dictionary at current level, got %s" %
                               type(data))
    # We check if this is the last level
    if self.__columns[col_index]["depth"] == self.__columns[-1]["depth"]:
      # We need to add the keys in the dictionary as they are
      for col in self.__columns[col_index:]:
        if col["id"] in data:
          prev_col_values[col["id"]] = data[col["id"]]
      self.__data.append(prev_col_values)
      return

    # We have a dictionary in an inner depth level.
    if not data.keys():
      # In case this is an empty dictionary, we add a record with the columns
      # filled only until this point.
      self.__data.append(prev_col_values)
    else:
      for key in sorted(data):
        col_values = dict(prev_col_values)
        col_values[self.__columns[col_index]["id"]] = key
        self._InnerAppendData(col_values, data[key], col_index + 1)

  def _PreparedData(self, sort_keys=()):
    """Prepares the data for enumeration - sorting it by sort_keys.

    Args:
      sort_keys: list of keys to sort by. Receives a single key to sort by, or
                 a list of keys for secondary sort. Each key can be a name of a
                 column, or a tuple containing the name of the column and the
                 sort direction as second parameter ("asc" or "desc").
                 For example: ("col1", "desc")

    Returns:
      The data sorted by the keys given.

    Raises:
      DataTableException: Sort direction not in 'asc' or 'desc'
    """
    if not sort_keys:
      return self.__data

    proper_sort_keys = []
    if isinstance(sort_keys, str) or (
        isinstance(sort_keys, tuple) and len(sort_keys) == 2 and
        sort_keys[1].lower() in ["asc", "desc"]):
      sort_keys = (sort_keys,)
    for key in sort_keys:
      if isinstance(key, str):
        proper_sort_keys.append((key, 1))
      elif (isinstance(key, (list, tuple)) and len(key) == 2 and
            key[1].lower() in ("asc", "desc")):
        proper_sort_keys.append((key[0], key[1].lower() == "asc" and 1 or -1))
      else:
        raise DataTableException("Expected tuple with second value: "
                                 "'asc' or 'desc'")

    def SortCmpFunc(row1, row2):
      """cmp function for sorted. Compares by keys and 'asc'/'desc' keywords."""
      for key, asc_mult in proper_sort_keys:
        cmp_result = asc_mult * cmp(row1.get(key), row2.get(key))
        if cmp_result:
          return cmp_result
      return 0

    return sorted(self.__data, cmp=SortCmpFunc)

  def ToJSCode(self, name, columns_order=None, order_by=()):
    """Writes the data table as a JS code string.

    This method writes a string of JS code that can be run to
    generate a DataTable with the specified data. Typically used for debugging
    only.

    Args:
      name: The name of the table. The name would be used as the DataTable's
            variable name in the created JS code.
      columns_order: Optional. Specifies the order of columns in the
                     output table. Specify a list of all column IDs in the order
                     in which you want the table created.
      order_by: Optional. Specifies the name of the column(s) to sort by, and
                (optionally) which direction to sort in. Default sort direction
                is asc. Following formats are accepted:
                "string_col_name"  -- For a single key in default (asc) order.
                ("string_col_name", "asc|desc") -- For a single key.
                [("col_1","asc|desc"), ("col_2","asc|desc")] -- For more than
                    one column, an array of tuples of (col_name, "asc|desc").

    Returns:
      A string of JS code that, when run, generates a DataTable with the given
      name and the data stored in the DataTable object.
      Example result:
        "var tab1 = new google.visualization.DataTable();
         tab1.addColumn('string', 'a', 'a');
         tab1.addColumn('number', 'b', 'b');
         tab1.addColumn('boolean', 'c', 'c');
         tab1.addRows(10);
         tab1.setCell(0, 0, 'a');
         tab1.setCell(0, 1, 1);
         tab1.setCell(0, 2, true);
         ...
         tab1.setCell(9, 0, 'c');
         tab1.setCell(9, 1, 3, '3$');
         tab1.setCell(9, 2, false);"

    Raises:
      DataTableException: The data does not match the type.
    """
    if not columns_order:
      columns_order = [col["id"] for col in self.__columns]
    col_dict = dict([(col["id"], col) for col in self.__columns])

    # We first create the table with the given name
    jscode = "var %s = new google.visualization.DataTable();\n" % name

    # We add the columns to the table
    for col in columns_order:
      jscode += "%s.addColumn('%s', '%s', '%s');\n" % (name,
                                                       col_dict[col]["type"],
                                                       col_dict[col]["label"],
                                                       col_dict[col]["id"])
    jscode += "%s.addRows(%d);\n" % (name, len(self.__data))

    # We now go over the data and add each row
    for (i, row) in enumerate(self._PreparedData(order_by)):
      # We add all the elements of this row by their order
      for (j, col) in enumerate(columns_order):
        if col not in row or row[col] is None:
          continue
        value = self.SingleValueToJS(row[col], col_dict[col]["type"])
        if isinstance(value, tuple):
          # We have a formatted value as well
          jscode += ("%s.setCell(%d, %d, %s, %s);\n" %
                     (name, i, j, value[0], value[1]))
        else:
          jscode += "%s.setCell(%d, %d, %s);\n" % (name, i, j, value)
    return jscode

  def ToJSon(self, columns_order=None, order_by=()):
    """Writes a JSON strong that can be used in a JS DataTable constructor.

    This method writes a JSON string that can be passed directly into a Google
    Visualization API DataTable constructor. Use this output if you are
    hosting the visualization HTML on your site, and want to code the data
    table in Python. Pass this string into the
    google.visualization.DataTable constructor, e.g,:
      ... on my page that hosts my visualization ...
      google.setOnLoadCallback(drawTable);
      function drawTable() {
        var data = new google.visualization.DataTable(_my_JSon_string, 0.5);
        myTable.draw(data);
      }

    Args:
      columns_order: Optional. Specifies the order of columns in the
                     output table. Specify a list of all column IDs in the order
                     in which you want the table created.
      order_by: Optional. Specifies the name of the column(s) to sort by, and
                (optionally) which direction to sort in. Default sort direction
                is asc. Following formats are accepted:
                "string_col_name"  -- For a single key in default (asc) order.
                ("string_col_name", "asc|desc") -- For a single key.
                [("col_1","asc|desc"), ("col_2","asc|desc")] -- For more than
                    one column, an array of tuples of (col_name, "asc|desc").

    Returns:
      A JSon constructor string to generate a JS DataTable with the data
      stored in the DataTable object.
      Example result (the result is without the newlines):
       {cols: [{id:'a',label:'a',type:'number'},
               {id:'b',label:'b',type:'string'},
              {id:'c',label:'c',type:'number'}],
        rows: [{c:[{v:1},{v:'z'},{v:2}]}, c:{[{v:3,f:'3$'},{v:'w'},{v:null}]}]}

    Raises:
      DataTableException: The data does not match the type.
    """
    if not columns_order:
      columns_order = [col["id"] for col in self.__columns]
    col_dict = dict([(col["id"], col) for col in self.__columns])

    # Creating the columns jsons
    cols_jsons = ["{id:'%(id)s',label:'%(label)s',type:'%(type)s'}" %
                  col_dict[col_id] for col_id in columns_order]

    # Creating the rows jsons
    rows_jsons = []
    for row in self._PreparedData(order_by):
      cells_jsons = []
      for col in columns_order:
        # We omit the {v:null} for a None value of the not last column
        value = row.get(col, None)
        if value is None and col != columns_order[-1]:
          cells_jsons.append("")
        else:
          value = self.SingleValueToJS(value, col_dict[col]["type"])
          if isinstance(value, tuple):
            # We have a formatted value as well
            cells_jsons.append("{v:%s,f:%s}" % value)
          else:
            cells_jsons.append("{v:%s}" % value)
      rows_jsons.append("{c:[%s]}" % ",".join(cells_jsons))

    # We now join the columns jsons and the rows jsons
    json = "{cols: [%s],rows: [%s]}" % (",".join(cols_jsons),
                                        ",".join(rows_jsons))
    return json

  def ToJSonResponse(self, columns_order=None, order_by=(), req_id=0):
    """Writes a table as a JSON response that can be returned as-is to a client.

    This method writes a JSON response to return to a client in response to a
    Google Visualization API query. This string can be processed by the calling
    page, and is used to deliver a data table to a visualization hosted on
    a different page.

    Args:
      columns_order: Optional. Passed straight to self.ToJSon().
      order_by: Optional. Passed straight to self.ToJSon().
      req_id: Optional. The response id, as retrieved by the request.

    Returns:
      A JSON response string to be received by JS the visualization Query
      object. This response would be translated into a DataTable on the
      client side.
      Example result (newlines added for readability):
       google.visualization.Query.setResponse({
          'version':'0.5', 'reqId':'0', 'status':'OK',
          'table': {cols: [...], rows: [...]}});

    Note: The URL returning this string can be used as a data source by Google
          Visualization Gadgets or from JS code.
    """
    table = self.ToJSon(columns_order, order_by)
    return ("google.visualization.Query.setResponse({'version':'0.5', "
            "'reqId':'%s', 'status':'OK', 'table': %s});") % (req_id, table)
