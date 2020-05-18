import nbformat
import copy

from nbconvert.preprocessors import ExecutePreprocessor
from .ExecutePreprocessors import OECPreprocessor, SelfReproducibilityCheckPreprocessor, StatusInspectionPreprocessor, DependencyPreprocessor

from .utils import *

class Analysizer():

    def __init__(self, notebook_path, notebook_file):
        self._nb_path = notebook_path.split('/')[-1]
        self._nb = nbformat.read(notebook_file, as_version=4)

        self._ep = None # ep is abbr for instance of ExecutePreprocessors
        self._py_version = None
        self._is_executable = None
        self._import_statemnets = None

        self._preceding_preapre()
        self._deep_copy_nb = copy.deepcopy(self._nb) # store deepcopy of the given notebook to avoid unexpected manipulation

    def _preceding_preapre(self):
        self._py_version = self._extract_py_version() # extract python version 

        # evaluate the name of kernel -> avoid the usage of inappropriate kernels like 'Python [Root]' or 'conda-root-py'
        try:
            kernal_name = self._nb['metadata']['kernelspec']['name']
            if kernal_name not in ['python2', 'python3']:
                self._nb['metadata']['kernelspec']['name'] = 'python3'
        except:
            pass 

        # clean redundant (unexecuted/markdown/raw) cells
        self._clean_redundant_cells()
        self._extract_import_statements()

    def _extract_py_version(self):
        meta_info = self._nb.metadata
        try:
            py_version_lst = meta_info['language_info']['version'].split('.')
            py_version = py_version_lst[0]+'.'+py_version_lst[1]
            return py_version
        except:
            return None

    def _extract_import_statements(self):
        import_statements = []
        for cell in self._nb.cells:
            statements = (cell.source).split('\n')
            for statement in statements:
                if any(substr in statement for substr in ['from', 'import']):
                    import_statements.append(statement)
        
        self._import_statemnets = import_statements

    def _clean_redundant_cells(self):
        invalid_cells_idx = []
        for (idx, cell) in enumerate(self._nb.cells):
            if not (cell.cell_type == 'code'):
                invalid_cells_idx.append(idx)
                continue
            elif cell.execution_count == None:
                invalid_cells_idx.append(idx)
                continue
            else:
                pass
        parsed_nb_cells = [item for (idx, item) in enumerate(
            self._nb.cells) if idx not in invalid_cells_idx]

        self._nb.cells = parsed_nb_cells

    def _set_ep_as_normal_mode(self):
        self._ep = ExecutePreprocessor()

    def _set_ep_as_OEC_mode(self):
        self._ep = OECPreprocessor()

    def _set_ep_as_dependency_mode(self, execution_order):
        self._ep = DependencyPreprocessor(execution_order)

    def _set_ep_check_repeatablility_mode(self, check_cell_idx, analyse_strategy, is_duplicate):
        self._ep = SelfReproducibilityCheckPreprocessor(check_cell_idx, analyse_strategy, is_duplicate)

    def _set_execution_order_for_ep_check_repeatablility_mode(self, execution_order):
        self._ep.set_execution_order(execution_order)

    def _set_ep_debug_mode(self, analyse_strategy, check_cell_idx):
        self._ep = StatusInspectionPreprocessor(analyse_strategy, check_cell_idx)

    def _set_execution_order_for_ep_debug_mode(self, execution_order):
        self._ep.set_execution_order(execution_order)

    def _execute_nb(self):
        self._ep.preprocess(self._nb, {'metadata': {'path': './'}})

    def _is_pandas_used(self, cells):
        whitelist = ['pandas', 'seaborn']
        is_pandas_used = False 

        for cell in cells:
            if not is_pandas_used:
                cell_statements = cell.source.split('\n')
                for statement in cell_statements:
                    if any(substr in statement for substr in whitelist):
                        is_pandas_used = True
                        break

        return is_pandas_used

    def _best_effort_repair(self):
        '''
        Fix statements, which contain randomness/time
        '''
        cells = copy.deepcopy(self._nb.cells)
        if len(cells) > 0:
            first_cell_source_code_lst = cells[0].source.split('\n')

            # fix_statement_lst = ['import random', 'random.seed(100)', 'import numpy', 'numpy.random.seed(100)']
            if not self._is_pandas_used(cells): 
                fix_statement_lst = ['from freezegun import freeze_time', 'freezer = freeze_time("2012-01-14 12:00:01")', 'freezer.start()', '%matplotlib inline', 'import random', 'random.seed(100)', 'import numpy', 'numpy.random.seed(100)']
            else:
                fix_statement_lst = ['%matplotlib inline', 'import random', 'random.seed(100)', 'import numpy', 'numpy.random.seed(100)']

            for fix_statement in (fix_statement_lst)[::-1]:
                first_cell_source_code_lst.insert(0, fix_statement)
            return_source_code = '\n'.join(first_cell_source_code_lst)
            cells[0].source = return_source_code
        
            self._nb.cells = cells 
       
    def return_py_version(self):
        return self._py_version

    def return_import_statements(self):
        return self._import_statemnets

    # This functionality is for experiment purpose
    def check_executability_on_all_potential_execution_paths(self, verbose):
        return True 

    # This functionality is for experiment purpose
    # Should not be called from users when Osiris is publicly released 
    def check_reproducibility_on_all_potential_execution_paths(self, verbose, match_pattern):
        execution_orders = get_all_potential_execution_orders(self._nb_path)

        results = []
        for execution_order in execution_orders:
            print(execution_order)
            self._nb = copy.deepcopy(self._deep_copy_nb)
            is_executable = False
            error = None

            try:
                self._set_ep_as_dependency_mode(execution_order)
                self._execute_nb()
                is_executable = True
            except Exception as e:
                error = e

            print('Executability'.ljust(40), ':', is_executable)
            self._is_executable = is_executable

            if verbose and (not is_executable):
                print(error)

            if is_executable:
                try:
                    self._nb = copy.deepcopy(self._deep_copy_nb)
                    if match_pattern == 'strong':
                        original_outputs = extract_outputs_based_on_dependency_order(self._nb.cells, execution_order)
                    elif match_pattern == 'weak':
                        self._set_ep_as_dependency_mode(execution_order)
                        self._execute_nb()
                        original_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
                    else:  # best-effort (PENDING)
                        self._best_effort_repair()
                        self._set_ep_as_OEC_mode()
                        self._execute_nb()
                        original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)


                    # Extract the executed outputs
                    self._nb = copy.deepcopy(self._deep_copy_nb)
                    if match_pattern == 'best_effort':
                        self._best_effort_repair()
                    self._set_ep_as_dependency_mode(execution_order)
                    self._execute_nb()
                    executed_outputs = extract_outputs_based_on_normal_order(self._nb.cells)

                    # Compare two outputs
                    matched_cell_idx = []
                    unmatched_cell_idx = []
                    unmatched_original_outputs = []
                    unmatched_executed_outputs = []
                    num_of_matched_cells, num_of_cells = 0, len(original_outputs)
                    for i in range(num_of_cells):
                        if original_outputs[i] == executed_outputs[i]:
                            num_of_matched_cells += 1
                            matched_cell_idx.append(i)
                        else:
                            unmatched_cell_idx.append(i)
                            unmatched_original_outputs.append(original_outputs[i])
                            unmatched_executed_outputs.append(executed_outputs[i])

                    # Return (print) the results
                    match_ratio = 0
                    if num_of_cells == 0:
                        match_ratio = 1
                    else:
                        match_ratio = num_of_matched_cells/num_of_cells

                    _ = extract_source_code_from_unmatched_cells(self._nb.cells, unmatched_cell_idx)
                    print('Reproducibility'.ljust(40), ':', "number of matched cells: {num_of_matched_cells} ; number of cells: {num_of_cells}".format(
                      num_of_matched_cells=num_of_matched_cells, num_of_cells=num_of_cells))
                    print('Reproducibility'.ljust(40), ':', "matched ratio: {match_ratio} ; index of matched cells: {matched_cell_idx}".format(
                      match_ratio=round(match_ratio, 3), matched_cell_idx=matched_cell_idx))

                    # Debug & Experiment purpose
                    # Print cells which are unmatched
                    if verbose:
                        self._nb = copy.deepcopy(self._deep_copy_nb)
                        print_source_code_of_unmatched_cells(self._nb.cells, 'dependency', unmatched_cell_idx, unmatched_original_outputs, unmatched_executed_outputs, execution_order)   
                except Exception as e:
                    print(e)
                    match_ratio = None
                    
                results.append(match_ratio)

        return results

    def check_executability(self, verbose, analyse_strategy):
        self._nb = copy.deepcopy(self._deep_copy_nb)
        is_executable, error = False, None
        
        try:
            if analyse_strategy == 'normal':
                self._set_ep_as_normal_mode()
            elif analyse_strategy == 'dependency':
                execution_order = get_execution_order(self._nb_path)
                self._set_ep_as_dependency_mode(execution_order)
            else:
                self._set_ep_as_OEC_mode()

            self._execute_nb()
            is_executable = True
        except Exception as e:
            error = e

        print('Executability'.ljust(40), ':', is_executable)
        self._is_executable = is_executable

        if verbose and (not is_executable):
            print(error)

        return is_executable

    def check_reproducibility(self, verbose, analyse_strategy, match_pattern):
        original_outputs, executed_outputs = None, None

        # Extract two outputs according to aanalyse_strategy and strong/weak match 
        if analyse_strategy == 'OEC':
            # Extract the original outputs 
            self._nb = copy.deepcopy(self._deep_copy_nb)

            if match_pattern == 'strong':
                original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)
            elif match_pattern == 'weak': 
                self._set_ep_as_OEC_mode()
                self._execute_nb()
                original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)
            else: # best-effort
                self._best_effort_repair() 
                self._set_ep_as_OEC_mode()
                self._execute_nb()
                original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)

            # Extract the executed outputs 
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if match_pattern == 'best_effort':
                self._best_effort_repair()

            self._set_ep_as_OEC_mode()
            self._execute_nb()
            executed_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)

        elif analyse_strategy == 'normal':

            # Extract the original outputs
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if match_pattern == 'strong':
                original_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
            elif match_pattern == 'weak':
                self._set_ep_as_normal_mode()
                self._execute_nb()
                original_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
            else: # best-effort 
                self._best_effort_repair() 
                self._set_ep_as_normal_mode()
                self._execute_nb()
                original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)

            # Extract the executed outputs
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if match_pattern == 'best_effort':
                self._best_effort_repair()
            self._set_ep_as_normal_mode()
            self._execute_nb()
            executed_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
        elif analyse_strategy == 'dependency':
            execution_order = get_execution_order(self._nb_path)
            print('Execution order:', execution_order)

            # Extract the original outputs
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if match_pattern == 'strong':
                original_outputs = extract_outputs_based_on_dependency_order(self._nb.cells, execution_order)
            elif match_pattern == 'weak':
                self._set_ep_as_dependency_mode(execution_order)
                self._execute_nb()
                original_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
            else:  # best-effort 
                self._best_effort_repair() 
                self._set_ep_as_dependency_mode(execution_order)
                self._execute_nb()
                original_outputs = extract_outputs_based_on_OEC_order(self._nb.cells)

            # Extract the executed outputs
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if match_pattern == 'best_effort':
                self._best_effort_repair()
            self._set_ep_as_dependency_mode(execution_order)
            self._execute_nb()
            executed_outputs = extract_outputs_based_on_normal_order(self._nb.cells)
        else:
            pass

        assert not (original_outputs is None)
        assert not (executed_outputs is None)
        assert len(original_outputs) == len(executed_outputs)

        # Compare two outputs
        matched_cell_idx = []
        unmatched_cell_idx = []
        unmatched_original_outputs = []
        unmatched_executed_outputs = []
        num_of_matched_cells, num_of_cells = 0, len(original_outputs)
        for i in range(num_of_cells):
            if original_outputs[i] == executed_outputs[i]:
                num_of_matched_cells += 1
                matched_cell_idx.append(i)
            else: 
                unmatched_cell_idx.append(i)
                unmatched_original_outputs.append(original_outputs[i])
                unmatched_executed_outputs.append(executed_outputs[i])

        # Return (print) the results
        match_ratio = 0
        if num_of_cells == 0:
            match_ratio = 1
        else:
            match_ratio = num_of_matched_cells/num_of_cells
        source_code_of_unmatched_cells = extract_source_code_from_unmatched_cells(self._nb.cells, unmatched_cell_idx)
        
        if len(unmatched_cell_idx) > 0:
            print('The first unmatched cell index:', unmatched_cell_idx[0])

        print('Reproducibility'.ljust(40), ':', "number of matched cells: {num_of_matched_cells} ; number of cells: {num_of_cells}".format(
            num_of_matched_cells=num_of_matched_cells, num_of_cells=num_of_cells))
        print('Reproducibility'.ljust(40), ':', "matched ratio: {match_ratio} ; index of matched cells: {matched_cell_idx}".format(
            match_ratio=round(match_ratio, 3), matched_cell_idx=matched_cell_idx))

        # Debug & Experiment purpose 
        # Print cells which are unmatched 
        if verbose:
            self._nb = copy.deepcopy(self._deep_copy_nb)
            if analyse_strategy == 'dependency':
                print_source_code_of_unmatched_cells(self._nb.cells, analyse_strategy, unmatched_cell_idx, unmatched_original_outputs, unmatched_executed_outputs, execution_order)   
            else:
                print_source_code_of_unmatched_cells(self._nb.cells, analyse_strategy, unmatched_cell_idx, unmatched_original_outputs, unmatched_executed_outputs)   

        return num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_of_unmatched_cells          

    def check_repeatablility(self, verbose, analyse_strategy):

        execution_order = None
        if analyse_strategy == 'dependency':
            execution_order = get_execution_order(self._nb_path)
        
        self._nb = copy.deepcopy(self._deep_copy_nb)
        num_of_cells = len(self._nb.cells)

        self_reproducible_cell_idx = []
        for i in range(num_of_cells):
            # +1 cuz we will insert a status inspection function as the first cell (with index 0)
            check_cell_idx = i + 1 

            # Get status variables if execute once
            is_duplicate = False
            self._nb = copy.deepcopy(self._deep_copy_nb)
            self._set_ep_check_repeatablility_mode(check_cell_idx, analyse_strategy, is_duplicate)
            if execution_order is not None:
                self._set_execution_order_for_ep_check_repeatablility_mode(execution_order)
            self._execute_nb()
            check_cell_outputs = self._nb.cells[check_cell_idx].outputs
            var_status_exe_once = check_cell_outputs[-1].data['text/plain']

            # Get status variables if execute twice
            self._nb = copy.deepcopy(self._deep_copy_nb)
            is_duplicate = True
            self._set_ep_check_repeatablility_mode(check_cell_idx, analyse_strategy, is_duplicate)
            if execution_order is not None:
                self._set_execution_order_for_ep_check_repeatablility_mode(execution_order)
            self._execute_nb()
            check_cell_outputs = self._nb.cells[check_cell_idx+1].outputs
            var_status_exe_twice = check_cell_outputs[-1].data['text/plain']

            # Check whether a cell is reproducible & Print
            is_self_reproducible = (var_status_exe_once == var_status_exe_twice)
            if verbose:
                print("Check the {cell_idx} th cell among {num_of_cells} cells. Self-reproducibility result: {Self_reproduciblity_result}".format(
                    cell_idx=check_cell_idx, num_of_cells=num_of_cells, Self_reproduciblity_result=is_self_reproducible))

            # Store results for further return
            if is_self_reproducible:
                self_reproducible_cell_idx.append(i)

        # Return
        num_of_self_reproducible_cells = len(self_reproducible_cell_idx)
        repeatablility_ratio = len(self_reproducible_cell_idx) / num_of_cells

        print('Self reproducibility'.ljust(40), ':', "number of repeatable cells: {num_of_self_reproducible_cells} ; number of cells: {num_of_cells}".format(
            num_of_self_reproducible_cells=num_of_self_reproducible_cells, num_of_cells=num_of_cells))
        print('Self reproducibility'.ljust(40), ':', "self-reproduciblity ratio: {repeatablility_ratio} ; index of repeatable cells: {self_reproducible_cell_idx}".format(
            repeatablility_ratio=round(repeatablility_ratio, 3), self_reproducible_cell_idx=self_reproducible_cell_idx))

        return num_of_self_reproducible_cells, num_of_cells, repeatablility_ratio, self_reproducible_cell_idx

    def _ep_get_number_of_statements(self):
        return self._ep.get_number_of_statements(self._nb)

    def _execute_nb_for_inspecting_status_of_certain_line(self, target_line_index):
        self._ep.preprocess_for_inspecting_status_of_certain_line(
            self._nb, {'metadata': {'path': './'}}, target_line_index)

    def check_status_difference_for_a_cell(self, analyse_strategy, check_cell_idx):
        # +1 cuz we will insert a status inspection function as the first cell (with index 0)
        check_cell_idx += 1
        first_var_status, second_var_status = None, None

        execution_order = None
        if analyse_strategy == 'dependency':
            execution_order = get_execution_order(self._nb_path)
            print('Execution order:', execution_order)

        self._nb = copy.deepcopy(self._deep_copy_nb)
        self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
        if execution_order is not None:
            self._set_execution_order_for_ep_debug_mode(execution_order)
        num_of_statements = self._ep_get_number_of_statements()

        # Check if the status of self-defined variables has been different before this cell
        self._nb = copy.deepcopy(self._deep_copy_nb)
        self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
        if execution_order is not None:
            self._set_execution_order_for_ep_debug_mode(execution_order)

        try:
            self._execute_nb_for_inspecting_status_of_certain_line(-1)
            check_cell_outputs = self._nb.cells[check_cell_idx].outputs
            first_var_status = check_cell_outputs[-1].data['text/plain']
        except:
            first_var_status = None
            
        self._nb = copy.deepcopy(self._deep_copy_nb)
        self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
        if execution_order is not None:
            self._set_execution_order_for_ep_debug_mode(execution_order)

        try:
            self._execute_nb_for_inspecting_status_of_certain_line(-1)
            check_cell_outputs = self._nb.cells[check_cell_idx].outputs
            second_var_status = check_cell_outputs[-1].data['text/plain']
        except:
            second_var_status = None

        if not (first_var_status == second_var_status):
            return -1 

        # Check if the status of self-defined variables has been different upon certain statement
        for i in range(num_of_statements):
            self._nb = copy.deepcopy(self._deep_copy_nb)
            self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
            if execution_order is not None:
                self._set_execution_order_for_ep_debug_mode(execution_order)

            try:
                self._execute_nb_for_inspecting_status_of_certain_line(i)
                check_cell_outputs = self._nb.cells[check_cell_idx].outputs
                first_var_status = check_cell_outputs[-1].data['text/plain']
            except Exception as e:
                first_var_status = None


            self._nb = copy.deepcopy(self._deep_copy_nb)
            self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
            if execution_order is not None:
                self._set_execution_order_for_ep_debug_mode(execution_order)
            try:
                self._execute_nb_for_inspecting_status_of_certain_line(i)
                check_cell_outputs = self._nb.cells[check_cell_idx].outputs
                second_var_status = check_cell_outputs[-1].data['text/plain']
            except Exception as e:
                second_var_status = None
            
            if first_var_status is None:
                first_var_status = {}
            if second_var_status is None:
                second_var_status = {}

            print(i,self._nb.cells[check_cell_idx].source.split('\n')[i], first_var_status, second_var_status)
            if not (first_var_status == second_var_status):
                self._nb = copy.deepcopy(self._deep_copy_nb)
                self._set_ep_debug_mode(analyse_strategy, check_cell_idx)
                if execution_order is not None:
                    self._set_execution_order_for_ep_debug_mode(execution_order)

                supicious_statement = None
                try:
                    self._execute_nb_for_inspecting_status_of_certain_line(i)
                    supicious_statement = self._nb.cells[check_cell_idx].source.split('\n')[i]
                except:
                    pass
                
                return (i, supicious_statement)

        # What if the status of self-defined variables remains the same through execution of this cell
        # return None to indicate unfound 
        return None


