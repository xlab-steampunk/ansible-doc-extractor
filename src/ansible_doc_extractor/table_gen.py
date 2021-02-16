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
        self.max_default_len = 0
        self.max_comment_len = 0
        self.head_node = None
        self.tail_node = None

    def _build_row_cells(self, data):
        cells = []
        for k, v in data_value.items():
            if k.lower() == "description":
                if len(v[0]) >  self.max_col_comment:
                    # Description element is wrapped in a list block though it is just a single entry
                    max_col_comment = len(v[0])
                cells.append(Cell(v[0], CELL_TYPE.COMMENT))
            elif k.lower() == "choices":
                cho_str = str(v[0])
                if len(cho_str) > self.max_col_default:
                    max_col_default = len(cho_str)
                cells.append(Cell(cho_str, CELL_TYPE.CHO_DEF))
            elif k.lower() != 'required': ## Therefore is the param column
                if len(k) >  self.max_col_param:
                    max_col_param = len(k)
                cells.append(Cell(k, CELL_TYPE.PARAM))
        return cells

    def _build_row_dll(self, curr_node, data):
        curr_node.cells = self._build_row_cells(data)
        if data.get('suboptions'):
            suboptions = data['suboptions'].keys()
            sub_head_opt = suboptions.pop()
            sub_head_node = RowNode()
            curr_node.next = sub_head_node
            sub_head_node.prev = curr_node
            
            _build_row_dll(head_opt, data['suboptions'][sub_head_opt])

            #next_node = RowNode()
            #curr_node.next_node = next_node
            #curr_node.prev_node = head_node
            for option in v.keys():
                #row_node.next = self.row_tail
                _build_row_dll(future_node, v[option])
                future_node = RowNode()
                future_node.prev = self.tail_node
                next_node.next = future_node
                future_node.prev = next_node
            self.tail_node = future_node
        else:
            # In this case the curr node was the last suboption
            self.tail_node = curr_node

    def _build_row_str(self):
        pass

    def build_table(self):
        pass