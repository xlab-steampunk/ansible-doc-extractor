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
    cells = []

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
        #fill = lambda x, y: x*y
        return " "



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

    def _build_row_cells(self, param, data, level):

        cells = []
        for i in range(level):
            cells.append(Cell(" ", CELL_TYPE.INDENT))
        param_len = len(param) + level
        if param_len > self.max_param_len:
            self.max_param_len = param_len
        cells.append(Cell(param, CELL_TYPE.PARAM))

        cho_def = ""
        if data.get("choices"):
            cho_def = str(data["choices"])
            if len(cho_def) > self.max_cho_def_len:
                self.max_cho_def_len = len(cho_def)
        cells.append(Cell(cho_def, CELL_TYPE.CHO_DEF))

        description = ""
        if data.get("description"):
            # Description element is wrapped in a list block though it is just a single entry
            description = data["description"][0]
            if len(description) > self.max_comment_len:
                self.max_comment_len = len(description)
        cells.append(Cell(description, CELL_TYPE.COMMENT))
        return cells

    def _build_row_str(self):
        pass

    def _add_spacer(self, future_node, level=0):
        row_spacer = RowSpacerNode("-", level)
        future_node.next_node = row_spacer
        row_spacer.prev_node = future_node

        # Update level of upper spacer to allow for column creation
        upper_spacer = row_spacer.prev_node.prev_node
        assert type(upper_spacer) == type(row_spacer)
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
        future_node.cells = self._build_row_cells(options[0], data[options[0]], level)
        row_spacer = self._add_spacer(future_node, level)

        tail_node = None
        for i in range(1, len(options)):
            param = options[i]
            param_val_dict = data[options[i]]

            tail_node = None # Overwrite tail_node if it wasn't the last

            future_node = RowNode()
            future_node.prev_node = row_spacer
            row_spacer.next_node = future_node
            future_node.cells = self._build_row_cells( param, param_val_dict, level)
            row_spacer = self._add_spacer(future_node)

            if param_val_dict.get('suboptions'):
                tail_node = self._build_row_dll(row_spacer, param_val_dict['suboptions'], level+1)
                if tail_node:
                    row_spacer = tail_node


        if tail_node:
            return tail_node
        return row_spacer

    def build_table(self, data):
                # TODO: self.head_node.cells = 
        row_spacer = RowSpacerNode("-", 3)
        head_node = RowNode()
        head_node.prev_node = row_spacer
        row_spacer.next_node = head_node
        head_dict = {'description': ['Comment'],
                     'choices': 'Choices/Defaults'}
        head_node.cells = self._build_row_cells('Parameters', head_dict, level=0)

        head_spacer = RowSpacerNode('=', 3)
        head_spacer.prev_node = head_node
        head_node.next_node = head_spacer

        if data:
            self._build_row_dll(head_spacer, data)

        table = []
        while head_node != None:
            table.append(head_node.__str__(self.max_param_len, self.max_cho_def_len, self.max_comment_len))
            head_node = head_node.next_node

        return table

