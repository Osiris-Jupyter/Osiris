from .analysizer import Analysizer
from .constants import *
from .utils import move_to_appropriate_location, distinguish_local_modules

class UserInterface():

    def __init__(self, path, execute_strategy, verbose, analyse_all_dependency=False):
        # Specify analyse settings
        self._nb_path = path 
        self._execute_strategy = execute_strategy
        self._verbose = verbose
        self.analyse_all_dependency = analyse_all_dependency

        # Create an analysizer, which takes the responsibility for the low-level manipulation 
        f = open(self._nb_path, 'r', encoding='utf-8')
        self.analysizer = Analysizer(path, f)

        # Extract python version
        self._py_version = self.analysizer.return_py_version()
        
        # Ensure both python version and strategy are valid
        assert self._py_version in VALID_PYTHON_VERSIONS
        assert self._execute_strategy in STRATEGIES
 
    def return_py_version(self):
        return self._py_version

    def return_import_statements(self):
        return self.analysizer.return_import_statements()

    def return_missing_packages(self):
        import_statements = self.analysizer.return_import_statements()
        return distinguish_local_modules(import_statements)

    def analyse_executability(self):
        move_to_appropriate_location(self._nb_path)

        if (self.analyse_all_dependency is True) and self._execute_strategy == 'dependency':
            lst_executabilities = self.analysizer.check_executability_on_all_potential_execution_paths(self._verbose)
            return lst_executabilities
        else: 
            is_executable = self.analysizer.check_executability(self._verbose, self._execute_strategy)
            return is_executable

    def analyse_reproducibility(self, match_pattern):
        assert match_pattern in MATCH_PATTERNS
        move_to_appropriate_location(self._nb_path)

        if (self.analyse_all_dependency is True) and self._execute_strategy == 'dependency':
            lst_of_matched_ratios = self.analysizer.check_reproducibility_on_all_potential_execution_paths(self._verbose, match_pattern)
            return lst_of_matched_ratios
        else: 
            num_of_matched_cells, num_of_cells, match_ratio, match_cell_idx, source_code_from_unmatched_cells = self.analysizer.check_reproducibility(
                self._verbose, self._execute_strategy, match_pattern)
            return num_of_matched_cells, num_of_cells, match_ratio, match_cell_idx, source_code_from_unmatched_cells

    def analyse_repeatablility(self):
        move_to_appropriate_location(self._nb_path)

        num_of_reproducible_cells, num_of_cells, reproducible_ratio, reproducible_cell_idx = self.analysizer.check_repeatablility(
            self._verbose, self._execute_strategy)
        return num_of_reproducible_cells, num_of_cells, reproducible_ratio, reproducible_cell_idx

    def analyse_status_difference_for_a_cell(self, cell_index):
        if cell_index == None:
            raise ValueError('cell_index argument should not be empty (None), please indicate the cell_index.')
    
        move_to_appropriate_location(self._nb_path)
        result = self.analysizer.check_status_difference_for_a_cell(self._execute_strategy, cell_index)
        
        if result is None:
            print('Statements in this cell did not cause any status difference of self-defined variables')
            return result
        elif result is -1:
            print('Status difference of self-defined variables may occur before any execution of statements in this cell')
            return result
        else: 
            problematic_statement_index, supicious_statement = result
            print('The potential statement for causing status difference is line', problematic_statement_index)
            print('--------------> ', supicious_statement)
            print('(Note that 0 indicates for the first line and empty lines are also included)')
      
            return problematic_statement_index

        
