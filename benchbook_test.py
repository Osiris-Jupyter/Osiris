import sys
import os

import warnings
import unittest
import Osiris
from Osiris.utils import risk_detect, distinguish_local_modules

test_execute_in_normal_strategy_nb_path = 'benchbook/test_execute_in_normal_strategy.ipynb'
test_execute_in_OEC_strategy_nb_path = 'benchbook/test_execute_in_OEC_strategy.ipynb'
test_on_case_require_executing_a_cell_twice_nb_path = 'benchbook/test_on_case_require_executing_a_cell_twice.ipynb'

test_on_magic_function_nb_path = 'benchbook/test_on_magic_function.ipynb'
test_import_statements_extraction_nb_path = 'benchbook/test_import_statements_extraction.ipynb'

test_reproducibility_with_strong_match_pattern_nb_path = 'benchbook/test_reproducibility_with_strong_match_pattern.ipynb'
test_dict_issue_nb_path = 'benchbook/test_dict_issue.ipynb'
test_random_nb_path = 'benchbook/test_random.ipynb'
test_time_nb_path = 'benchbook/test_time.ipynb'
test_tiny_float_difference_nb_path = 'benchbook/test_tiny_float_difference.ipynb'
test_warning_nb_path = 'benchbook/test_warning.ipynb'
test_exclaimation_mark_nb_path = 'benchbook/test_exclaimation_mark.ipynb'

# Case 1: ipynb file in the same directory as Osiris; image in the same directory as ipynb file
test_relative_path_1_nb_path = 'test_relative_path_1.ipynb' 
# Case 2: ipynb file in the same directory as Osiris; image NOT in the same directory as ipynb file
test_relative_path_2_nb_path = 'test_relative_path_2.ipynb'
# Case 3: ipynb file NOT in the same directory as Osiris; image in the same directory as ipynb file
test_relative_path_3_nb_path = 'benchbook/test_relative_path_3.ipynb'
# Case 4: ipynb file NOT in the same directory as Osiris; image NOT in the same directory as ipynb file
test_relative_path_4_nb_path = 'benchbook/test_relative_path_4.ipynb'

# compound_assignment_operators refer to operators like +=, -=, *=, ...
test_compound_assignment_operators_nb_path = 'benchbook/test_compound_assignment_operators.ipynb'
test_package_dependency_nb_path = 'benchbook/test_package_dependency.ipynb'
test_irrational_path_nb_path = 'benchbook/test_irrational_path.ipynb'
test_implicit_var_definition_nb_path = 'benchbook/test_implicit_var_definition.ipynb'

test_multiple_execution_paths_nb_path = 'benchbook/test_multiple_execution_paths.ipynb'

# Global setting
verbose = True
root_path = os.getcwd()

class Benchbook(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        os.chdir(root_path)

    def test_execute_in_normal_strategy(self):
        interface = Osiris.UserInterface(test_execute_in_normal_strategy_nb_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_execute_in_OEC_strategy(self):
        interface = Osiris.UserInterface(test_execute_in_OEC_strategy_nb_path, 'OEC', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_on_case_require_executing_a_cell_twice(self):
        interface = Osiris.UserInterface(test_on_case_require_executing_a_cell_twice_nb_path, 'OEC', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, False)

    def test_on_magic_function(self):
        interface = Osiris.UserInterface(test_on_magic_function_nb_path, 'dependency', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('strong')
        self.assertEqual(num_of_cells, 2)

    def test_import_statements_extraction(self):
        interface = Osiris.UserInterface(test_import_statements_extraction_nb_path, 'normal', verbose)
        import_statements = interface.return_import_statements()
        self.assertEqual(import_statements, ['import time', 'import random', 'from random import randint'])

    def test_on_self_defined_packages_detection(self):
        # random case 
        statements = ['from random import randint',
                      'import sys, os',
                      'import time', 
                      'import warning', 
                      'import unittest']
        results = distinguish_local_modules(statements)
        self.assertEqual(results, [])

        # test top 10 packages -> refer to the paper 
        statements = ['import numpy as np',
                      'from matplotlib import pyplot as plt',
                      'import matplotlib.pyplot as plt',
                      'import pandas', 
                      'import sklearn', 
                      'import os, time, math', 
                      'import scipy', 
                      'import seaborn', 
                      'import IPython']
        results = distinguish_local_modules(statements)
        self.assertEqual(results, [])

        # A package which does not exist 
        statements = ['from a import b',
                      'import a',
                      'import c'] 
        results = distinguish_local_modules(statements)
        self.assertTrue(results == ['a', 'c'] or results == ['c', 'a'])

        # A package which exist in the same directory (PENDING)
        statements = ['import Osiris',
                      'from Osiris.utils import get_dependency_matrix, risk_detect, distinguish_local_modules']
        results = distinguish_local_modules(statements)
        self.assertEqual(results, [])

    '''
    The following 7 unit tests aim to test on reproducibility, which may cause challenges for Osiris to reproduce outputs 
    '''
    def test_reproducibility_with_strong_match_pattern(self):
        interface = Osiris.UserInterface(test_reproducibility_with_strong_match_pattern_nb_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('strong')
        self.assertEqual(match_ratio, 1.0)

    def test_dict_issue(self):
        interface = Osiris.UserInterface(test_dict_issue_nb_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('weak')
        self.assertEqual(match_ratio, 1.0)

    def test_random(self):
        detect_result, info = risk_detect(test_random_nb_path)
        self.assertEqual(detect_result, False)
        self.assertEqual(info, 'inadvisable usage')

    def test_time(self):
        interface = Osiris.UserInterface(test_time_nb_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 0)

    def test_tiny_float_difference(self):
        interface = Osiris.UserInterface(test_tiny_float_difference_nb_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('strong')
        self.assertEqual(match_ratio, 1.0)

    def test_warning(self):
        interface = Osiris.UserInterface(test_warning_nb_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_reproducibility('weak')
        self.assertEqual(match_ratio, 1.0)

    def test_exclaimation_mark(self):
        detect_result, info = risk_detect(test_exclaimation_mark_nb_path)
        self.assertEqual(detect_result, False)
        self.assertEqual(info, 'SyntaxError')

    '''
    The following 4 unit tests aim to test on relative path issues 
    '''
    @unittest.skip
    def test_relative_path_1(self):
        interface = Osiris.UserInterface(test_relative_path_1_nb_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    @unittest.skip
    def test_relative_path_2(self):
        interface = Osiris.UserInterface(test_relative_path_2_nb_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_relative_path_3(self):
        interface = Osiris.UserInterface(test_relative_path_3_nb_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_relative_path_4(self):
        interface = Osiris.UserInterface(test_relative_path_3_nb_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

if __name__ == '__main__':
    unittest.main()
