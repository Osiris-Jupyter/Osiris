from __future__ import absolute_import
from nbconvert.preprocessors import ExecutePreprocessor

EXTRACT_FUNC_STR = "def extractVars():\n    variables_set = {}\n    tmp = globals().copy()\n    for k, v in tmp.items():\n        con_1 = not k.startswith('_')\n        con_2 = not k in ['In', 'Out', 'get_ipython', 'exit', 'quit']\n        con_3 = type(v) in [int, complex, bool, float, str, list, set, dict, tuple]\n        con_4 = not('<' in str(v) and '>' in str(v) and 'at' in str(v))\n        if con_1 and con_2 and con_4:\n            variables_set[k] = v\n    \n    return variables_set"

class OECPreprocessor(ExecutePreprocessor):

    def __init__(self):
        super(ExecutePreprocessor, self).__init__()

    def preprocess(self, nb, resources):
        copy_nb_cells = nb.cells

        execution_count_lst = [cell.execution_count for cell in copy_nb_cells]
        OEO = sorted(range(len(execution_count_lst)),
                     key=lambda k: execution_count_lst[k])
        parsed_nb_cells = [copy_nb_cells[idx] for idx in OEO]
        if len(parsed_nb_cells) > 0:
            parsed_nb_cells[0].source = "import warnings\nwarnings.filterwarnings('ignore')\n" + parsed_nb_cells[0].source

        nb.cells = parsed_nb_cells
        return super(OECPreprocessor, self).preprocess(nb, resources)


class DependencyPreprocessor(ExecutePreprocessor):
    def __init__(self, execution_order):
        super(ExecutePreprocessor, self).__init__()
        self._execution_order = execution_order

    def preprocess(self, nb, resources):
        copy_nb_cells = nb.cells

        parsed_nb_cells = [copy_nb_cells[idx] for idx in self._execution_order]
        parsed_nb_cells[0].source = "import warnings\nwarnings.filterwarnings('ignore')\n" + parsed_nb_cells[0].source

        nb.cells = parsed_nb_cells
        return super(DependencyPreprocessor, self).preprocess(nb, resources)


class SelfReproducibilityCheckPreprocessor(ExecutePreprocessor):

    def __init__(self, check_cell_idx, analyse_strategy, is_duplicate):
        super(ExecutePreprocessor, self).__init__()
        self.check_cell_idx = check_cell_idx
        self.analyse_strategy = analyse_strategy
        self.is_duplicate = is_duplicate
        self.execution_order = None

    def set_execution_order(self, execution_order):
        self.execution_order = execution_order

    def preprocess(self, nb, resources):
        copy_nb_cells = nb.cells

        # Adjust the order of cells for different analyse strategies 
        if self.analyse_strategy == 'normal':
            parsed_nb_cells = copy_nb_cells.copy()
        elif self.analyse_strategy == 'OEC':
            execution_count_lst = [cell.execution_count for cell in copy_nb_cells]
            OEO = sorted(range(len(execution_count_lst)),
                        key=lambda k: execution_count_lst[k])
            parsed_nb_cells = [copy_nb_cells[idx] for idx in OEO]
        else: # dependency 
            parsed_nb_cells = [copy_nb_cells[idx] for idx in self.execution_order]

        # Insert an function at the beginning of the notebook to inspect the status 
        var_extract_fun_cell = parsed_nb_cells[0].copy()
        var_extract_fun_cell.source = EXTRACT_FUNC_STR
        parsed_nb_cells.insert(0, var_extract_fun_cell)

        # Modify source code of cells to monitor status of self-defined variables 
        if self.is_duplicate:
            copy_cell = parsed_nb_cells[self.check_cell_idx]
            copy_cell = copy_cell.copy()
            parsed_nb_cells.insert(self.check_cell_idx+1, copy_cell)
            parsed_nb_cells[self.check_cell_idx+1].source += "\nextractVars()"
            parsed_nb_cells[0].source = "import warnings\nwarnings.filterwarnings('ignore')\n" + parsed_nb_cells[0].source
            nb.cells = parsed_nb_cells[:self.check_cell_idx+2]
        else:
            parsed_nb_cells[self.check_cell_idx].source += "\nextractVars()"
            parsed_nb_cells[0].source = "import warnings\nwarnings.filterwarnings('ignore')\n" + parsed_nb_cells[0].source
            nb.cells = parsed_nb_cells[:self.check_cell_idx+1]

        return super(SelfReproducibilityCheckPreprocessor, self).preprocess(nb, resources)


class StatusInspectionPreprocessor(ExecutePreprocessor):
    
    def __init__(self, analyse_strategy, check_cell_idx):
        super(ExecutePreprocessor, self).__init__()
        self.check_cell_idx = check_cell_idx
        self.analyse_strategy = analyse_strategy
        self.execution_order = None
        self.whitelist = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'def', 'with', 'class']

    def set_execution_order(self, execution_order):
        self.execution_order = execution_order

    def get_number_of_statements(self, nb):
        copy_nb_cells = nb.cells

        # Adjust the order of cells for different analyse strategies
        if self.analyse_strategy == 'normal':
            parsed_nb_cells = copy_nb_cells.copy()
        elif self.analyse_strategy == 'OEC':
            execution_count_lst = [
                cell.execution_count for cell in copy_nb_cells]
            OEO = sorted(range(len(execution_count_lst)),
                         key=lambda k: execution_count_lst[k])
            parsed_nb_cells = [copy_nb_cells[idx] for idx in OEO]
        else:  # dependency
            parsed_nb_cells = [copy_nb_cells[idx] for idx in self.execution_order]

        # Insert an function at the beginning of the notebook to inspect the status
        var_extract_fun_cell = parsed_nb_cells[0].copy()
        var_extract_fun_cell.source = EXTRACT_FUNC_STR
        parsed_nb_cells.insert(0, var_extract_fun_cell)

        # Modify source code of cells to monitor status of self-defined variables line by line
        copy_cell = parsed_nb_cells[self.check_cell_idx]
        copy_cell = copy_cell.copy()
        statements = (copy_cell.source).split('\n')

        return len(statements)

    def preprocess_for_inspecting_status_of_certain_line(self, nb, resources, target_line_index):
        copy_nb_cells = nb.cells

        # Adjust the order of cells for different analyse strategies 
        if self.analyse_strategy == 'normal':
            parsed_nb_cells = copy_nb_cells.copy()
        elif self.analyse_strategy == 'OEC':
            execution_count_lst = [cell.execution_count for cell in copy_nb_cells]
            OEO = sorted(range(len(execution_count_lst)),
                        key=lambda k: execution_count_lst[k])
            parsed_nb_cells = [copy_nb_cells[idx] for idx in OEO]
        else: # dependency 
            parsed_nb_cells = [copy_nb_cells[idx]
                               for idx in self.execution_order]


        # Insert an function at the beginning of the notebook to inspect the status 
        var_extract_fun_cell = parsed_nb_cells[0].copy()
        var_extract_fun_cell.source = EXTRACT_FUNC_STR
        parsed_nb_cells.insert(0, var_extract_fun_cell)

        # Modify source code of cells to monitor status of self-defined variables line by line 
        copy_cell = parsed_nb_cells[self.check_cell_idx]
        copy_cell = copy_cell.copy()
        statements = (copy_cell.source).split('\n')

        # CASE 1: Check for status difference before executing this cell 
        if target_line_index == -1: 
            new_source_code_for_the_cell = []
            new_source_code_for_the_cell.append("extractVars()")

        # CASE 2: Check for status difference until certain statement 
        else:
            new_source_code_for_the_cell = [] 
            for line_index, statement in enumerate(statements):
                new_source_code_for_the_cell.append(statement)
                if line_index == target_line_index:
                    num_of_leading_spaces = len(statement) - len(statement.lstrip())
                    num_of_extract_vars_func = len("pass")
                    num_of_identation = num_of_leading_spaces+num_of_extract_vars_func

                    if any(substr in statement for substr in self.whitelist):
                        num_of_identation += 4

                    new_source_code_for_the_cell.append("pass".rjust(num_of_identation))
                    new_source_code_for_the_cell.append("extractVars()")
                    break

        new_source_code = '\n'.join(new_source_code_for_the_cell)
        parsed_nb_cells[self.check_cell_idx].source = new_source_code
        parsed_nb_cells[0].source = "import warnings\nwarnings.filterwarnings('ignore')\n" + parsed_nb_cells[0].source
        nb.cells = parsed_nb_cells[:self.check_cell_idx+1]
        return super(StatusInspectionPreprocessor, self).preprocess(nb, resources)

