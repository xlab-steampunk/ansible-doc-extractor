#    Copyright 2021, A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import enum

CELL_TYPE = enum.Enum('CELL_TYPE', 'INDENT PARAM CHO_DEF COMMENT')


class IncorrectCellTypeException(Exception):

    def __init__(self, cell_type):
        message = f"Provided cell type {cell_type} does not exist in CELL_TYPE enum"
        super().__init__(message)


class ListNode(object):

    def __init__(self, next_node=None, prev_node=None):
        self.next_node = next_node
        self.prev_node = prev_node


class RowNode(ListNode):

    def __init__(self):
        self.cells = []

    def __str__(self, max_param_len, max_cho_def_len, max_comment_len):
        row_str = "|"
        indent_cnt = len(self.cells) - 3 # If we have extra cells then these are for suboption indenting
        assert indent_cnt >= 0
        for i in range(indent_cnt):
            indent_cell_str = " {} |".format(self.cells[i])
            row_str += indent_cell_str
            max_param_len -= len(indent_cell_str)

        param = str(self.cells[indent_cnt])
        cho_def = str(self.cells[indent_cnt + 1])
        comment = str(self.cells[indent_cnt + 2])

        cell_padding = lambda x, y: x + " " * y
        col1_str = cell_padding(param, abs(len(param) - max_param_len))
        col2_str = cell_padding(cho_def, abs(len(cho_def) - max_cho_def_len))
        col3_str = cell_padding(comment, abs(len(comment) - max_comment_len))

        row_str += " {} | {} | {} |".format(col1_str, col2_str, col3_str)
        return row_str


class RowSpacerNode(ListNode):
    
    def __init__(self, spacer_char, level=0, next_node=None, prev_node=None):
        self.spacer_char = spacer_char
        self.level = level
        super().__init__(next_node, prev_node)

    def __str__(self, max_param_len, max_cho_def_len, max_comment_len):
        fill = lambda x, y: x*y

        row_spacer = "+"
        for i in range(self.level):
            indent_spacer = fill(self.spacer_char, 3)
            row_spacer += indent_spacer + "+"
            max_param_len -= len(indent_spacer) + 1

        col1_fill = fill(self.spacer_char, max_param_len + 2)
        col2_fill = fill(self.spacer_char, max_cho_def_len + 2)
        col3_fill = fill(self.spacer_char, max_comment_len + 2)
        row_spacer += "{}+{}+{}+".format(col1_fill, col2_fill, col3_fill)

        return row_spacer



class Cell(object):

    def __init__(self, content, cell_type):
        self.content = content
        # TODO: Check if provided type is in ENUM and raise error otherwise
        if cell_type not in list(CELL_TYPE):
            raise IncorrectCellTypeException(cell_type)
        self.cell_type = cell_type

    def __str__(self):
        return str(self.content)


class Table(object):

    def __init__(self):
        self.max_param_len = 0
        self.max_cho_def_len = 0
        self.max_comment_len = 0
        self.max_level = 0
        self.head_node = None
        self.tail_node = None

    def _build_row(self, future_node, param, data, level):

        # Create list of indent cells
        indent_cells = []
        for i in range(level):
            indent_cells.append(Cell(" ", CELL_TYPE.INDENT))
        future_node.cells.extend(indent_cells)

        param_len = len(param) + level*4 # |---| is 5 char, but first | is expected. So only need 4 extra char per level
        if param_len > self.max_param_len:
            self.max_param_len = param_len
        future_node.cells.append(Cell(param, CELL_TYPE.PARAM))

        cho_def = ""
        if data.get("choices"):
            cho_def = str(data["choices"])
            if len(cho_def) > self.max_cho_def_len:
                self.max_cho_def_len = len(cho_def)
        future_node.cells.append(Cell(cho_def, CELL_TYPE.CHO_DEF))

        description = ""
        if data.get("description"):
            # Description element is wrapped in a list block though it is just a single entry
            description = data["description"][0]
            if len(description) > self.max_comment_len:
                self.max_comment_len = len(description)
        future_node.cells.append(Cell(description, CELL_TYPE.COMMENT))

        # Add extra RowNode for required tag
        if data.get("required") == True:
            required_node = RowNode()
            required_node.cells = indent_cells
            required_node.cells.append(Cell("required", CELL_TYPE.PARAM))
            required_node.cells.append(Cell(" ", CELL_TYPE.CHO_DEF))
            required_node.cells.append(Cell(" ", CELL_TYPE.COMMENT))

            future_node.next_node = required_node
            required_node.prev_node = future_node
            future_node = required_node

        return future_node

    def _add_spacer(self, future_node, level=0):
        row_spacer = RowSpacerNode("-", level)
        future_node.next_node = row_spacer
        row_spacer.prev_node = future_node

        # Update level of upper spacer to allow for column creation
        upper_spacer = row_spacer.prev_node.prev_node
        if type(upper_spacer) != type(row_spacer):
            upper_spacer = upper_spacer.prev_node

        level_delta = row_spacer.level - upper_spacer.level
        if level_delta > 0:
            upper_spacer.level += level_delta
        return row_spacer

    def _build_row_dll(self, head_node, data, level=0):
        if level > self.max_level:
            self.max_level = level
        future_node = RowNode()
        head_node.next_node = future_node
        future_node.prev_node = head_node

        options = list(data.keys())
        future_node = self._build_row(future_node, options[0], data[options[0]], level)
        row_spacer = self._add_spacer(future_node, level)

        tail_node = None
        for i in range(1, len(options)):
            param = options[i]
            param_val_dict = data[options[i]]

            tail_node = None # Overwrite tail_node if it wasn't the last

            future_node = RowNode()
            future_node.prev_node = row_spacer
            row_spacer.next_node = future_node
            future_node = self._build_row(future_node, param, param_val_dict, level)
            row_spacer = self._add_spacer(future_node, level)

            if param_val_dict.get('suboptions'):
                tail_node = self._build_row_dll(row_spacer, param_val_dict['suboptions'], level+1)
                if tail_node:
                    row_spacer = tail_node


        if tail_node:
            return tail_node
        return row_spacer

    def build_table(self, data):
        head_node = RowSpacerNode("-")
        head_row_node = RowNode()
        head_row_node.prev_node = head_node
        head_node.next_node = head_row_node
        head_dict = {'description': ['Comment'],
                     'choices': 'Choices/Defaults'}

        head_row_node = self._build_row(head_row_node, 'Parameters', head_dict, level=0)

        head_spacer = RowSpacerNode('=')
        head_spacer.prev_node = head_row_node
        head_row_node.next_node = head_spacer

        if data:
            self._build_row_dll(head_spacer, data)

        table = []
        while head_node != None:
            table.append(head_node.__str__(self.max_param_len, self.max_cho_def_len, self.max_comment_len))
            head_node = head_node.next_node

        return table

