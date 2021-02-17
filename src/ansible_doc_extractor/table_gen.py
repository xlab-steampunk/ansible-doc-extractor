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

CELL_TYPE = enum.Enum('CELL_TYPE', 'PARAM CHO_DEF COMMENT')

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


class RowSpacerNode(ListNode):
    
    def __init__(self, spacer_char, cell_cnt=0, next_node=None, prev_node=None):
        self.spacer_char = spacer_char
        self.cell_cnt = cell_cnt
        super().__init__(next_node, prev_node)


class Cell(object):

    def __init__(self, content, cell_type):
        self.content = content
        # TODO: Check if provided type is in ENUM and raise error otherwise
        if cell_type not in list(CELL_TYPE):
            raise IncorrectCellTypeException(cell_type)
        self.cell_type = cell_type


class Table(object):

    def __init__(self):
        self.max_param_len = 0
        self.max_cho_def_len = 0
        self.max_comment_len = 0
        self.head_node = None
        self.tail_node = None

    def _build_row_cells(self, param, data):
        cells = []
        
        if len(param) > self.max_param_len:
            self.max_param_len = len(param)
            cells.append(Cell(param, CELL_TYPE.PARAM))

        description = ""
        if data.get("description"):
            # Description element is wrapped in a list block though it is just a single entry
            description = data["description"][0]
            if len(description) > self.max_comment_len:
                self.max_comment_len = len(description)
        cells.append(Cell(description, CELL_TYPE.COMMENT))

        cho_def = ""
        if data.get("choices"):
            cho_def = str(data["choices"])
            if len(cho_def) > self.max_cho_def_len:
                self.max_cho_def_len = len(cho_def)
        cells.append(Cell(cho_def, CELL_TYPE.CHO_DEF))

        return cells

    def _build_row_str(self):
        pass

    def _build_row_dll(self, head_node, data, level=0):
        future_node = RowNode()
        head_node.next_node = future_node
        future_node.prev_node = head_node

        for k, v in data.items():
            future_node.cells = self._build_row_cells(k, v)
            if v.get('suboptions'):
                tail_node = self._build_row_dll(future_node, v['suboptions'], level+1)
                #TODO: Add spacer
                #spacer = RowSpacerNode("=", 0)
                future_node = RowNode()
                tail_node.next_node = future_node
                future_node.prev_node = tail_node
            else:
                #TODO: Add spacer
                #spacer = RowSpacerNode("=", 0)

                temp_node = future_node
                future_node = RowNode()
                temp_node.next_node = future_node
                future_node.prev_node = temp_node
            future_node.next_node = None # Ensure that no next is set if at the end
        return future_node

    def build_table(self, data):
        header_spacer = RowSpacerNode("=", 3)
        self.head_node = RowNode()
        self.head_node.prev_node = header_spacer
        header_spacer.next_node = self.head_node
        row_spacer = RowSpacerNode('-', 3)
        row_spacer.prev_node = self.head_node
        self.head_node.next_node = row_spacer
        # TODO: self.head_node.cells = 
        if data:
            self._build_row_dll(self.head_node, data)
