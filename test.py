import sys
import os

import warnings
import unittest
import Osiris

from Osiris.utils import return_fix_statement_for_random_statement 

test_executability_notebook_path = 'tests/test_executability.ipynb'
test_reproducibility_notebook_path = 'tests/test_reproducibility.ipynb'
test_best_effort_notebook_path = 'tests/test_best_effort.ipynb' # It's for sub testset among reproducibility test set 
test_repeatablility_notebook_path = 'tests/test_self_reproducibility.ipynb'
test_debug_for_a_cell_notebook_path = 'tests/test_debug_for_a_cell.ipynb'

test_IPythonDisplay_notebook_path = 'tests/test_IPythonDisplay.ipynb'
test_Matplotlib_notebook_path = 'tests/test_Matplotlib.ipynb'

# Global setting 
verbose = False
root_path = os.getcwd()

class TestOsiris(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        os.chdir(root_path)

    '''
    The following 3 unit tests focus executability
    '''
    def test_normal_executability(self):
        interface = Osiris.UserInterface(test_executability_notebook_path, 'normal', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_OEC_executability(self):
        interface = Osiris.UserInterface(test_executability_notebook_path, 'OEC', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    def test_dependency_executability(self):
        interface = Osiris.UserInterface(test_executability_notebook_path, 'dependency', verbose)
        is_executable = interface.analyse_executability()
        self.assertEqual(is_executable, True)

    '''
    The following 9 unit tests focus reproducibility
    '''
    def test_top_down_strong_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('strong')
        self.assertEqual(num_of_matched_cells, 6)
        self.assertEqual(num_of_cells, 8)

    def test_top_down_weak_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    def test_OEC_strong_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'OEC', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('strong')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    def test_OEC_weak_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'OEC', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    def test_dependency_strong_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'dependency', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('strong')
        self.assertEqual(num_of_matched_cells, 6) # BUGGY STATEMENT 
        self.assertEqual(num_of_cells, 8)

    def test_dependency_weak_reproducibility(self):
        interface = Osiris.UserInterface(test_reproducibility_notebook_path, 'dependency', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    # For best_effort match pattern, we carefully crafted a notebook for testing best_effort match pattern 
    def test_top_down_best_effort_reproducibility(self):
        interface = Osiris.UserInterface(test_best_effort_notebook_path, 'normal', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('best_effort')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    def test_OEC_best_effort_reproducibility(self):
        interface = Osiris.UserInterface(test_best_effort_notebook_path, 'OEC', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('best_effort')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)
        
    def test_dependency_best_effort_reproducibility(self):
        interface = Osiris.UserInterface(test_best_effort_notebook_path, 'dependency', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('best_effort')
        self.assertEqual(num_of_matched_cells, 8)
        self.assertEqual(num_of_cells, 8)

    '''
    The following 3 unit tests focus repeatablility
    '''
    def test_top_down_repeatablility(self):
        interface = Osiris.UserInterface(test_repeatablility_notebook_path, 'normal', verbose)
        num_of_reproducible_cells, num_of_cells, _, reproducible_cell_idx = interface.analyse_repeatablility()
        self.assertEqual(num_of_reproducible_cells, 2)
        self.assertEqual(num_of_cells, 4)
        self.assertEqual(reproducible_cell_idx, [0, 3])

    def test_OEC_repeatablility(self):
        interface = Osiris.UserInterface(test_repeatablility_notebook_path, 'OEC', verbose)
        num_of_reproducible_cells, num_of_cells, _, reproducible_cell_idx = interface.analyse_repeatablility()
        self.assertEqual(num_of_reproducible_cells, 2)
        self.assertEqual(num_of_cells, 4)
        self.assertEqual(reproducible_cell_idx, [0, 1])

    def test_dependency_repeatablility(self):
        interface = Osiris.UserInterface(test_repeatablility_notebook_path, 'dependency', verbose)
        num_of_reproducible_cells, num_of_cells, _, _ = interface.analyse_repeatablility()
        self.assertEqual(num_of_reproducible_cells, 2)
        self.assertEqual(num_of_cells, 4)

    '''
    The following 3 unit tests focus status difference inspection
    '''
    def test_top_down_debug_for_a_cell(self):
        interface = Osiris.UserInterface(test_debug_for_a_cell_notebook_path, 'normal', verbose)
        problematic_statement_index = interface.analyse_status_difference_for_a_cell(1)
        self.assertEqual(problematic_statement_index, 10)

    def test_OEC_debug_for_a_cell(self):
        interface = Osiris.UserInterface(test_debug_for_a_cell_notebook_path, 'OEC', verbose)
        problematic_statement_index = interface.analyse_status_difference_for_a_cell(2)
        self.assertEqual(problematic_statement_index, 10)

    def test_dependency_debug_for_a_cell(self):
        interface = Osiris.UserInterface(test_debug_for_a_cell_notebook_path, 'dependency', verbose)
        problematic_statement_index = interface.analyse_status_difference_for_a_cell(1)
        self.assertEqual(problematic_statement_index, 10)

    '''
    The following 2 unit tests focus on the correctness of Osiris for images 
    '''
    def test_image_IPythonDisplay(self):
        interface = Osiris.UserInterface(test_IPythonDisplay_notebook_path, 'OEC', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 1)
        self.assertEqual(num_of_cells, 1)

    def test_image_Matplotlib(self):
        interface = Osiris.UserInterface(test_Matplotlib_notebook_path, 'OEC', verbose)
        num_of_matched_cells, num_of_cells, _, _, _ = interface.analyse_reproducibility('weak')
        self.assertEqual(num_of_matched_cells, 2)
        self.assertEqual(num_of_cells, 2)

    '''
    Below unit test focus on the util func: return_fix_statement
    Note that this unit test should be removed in the future
    '''
    def test_return_fix_statement(self):
        print()
        # 1
        statement, import_statement_lst = 'a = random.randint(0, 3)', ['import random']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 2
        statement, import_statement_lst = 'numpy.random.randint(5)', ['import numpy']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 3
        statement, import_statement_lst = 'np.random.randint(5)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 4
        statement, import_statement_lst = 'd = np.random.normal(0, 0.2, 5000)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 5
        statement, import_statement_lst = "datos = {\n    'valores': np.random.randn(100),\n    'frecuencia': dt.timedelta(minutes = 10),\n    'fecha_inicial': dt.datetime(2016, 1, 1, 0, 0),\n    'parametro': 'wind_speed',\n    'unidades': 'm/s'\n}", ['import numpy as np'] 
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 6
        statement, import_statement_lst = '    y_var2 = np.random.randint(5, 8, 10)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 7
        statement, import_statement_lst = '    x_ = random.random()', ['import random']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 8
        statement, import_statement_lst = '    s_ = scale*random.random()', ['import random']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 9
        statement, import_statement_lst =  'X = np.random.uniform(0.,1.,N)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 10
        statement, import_statement_lst = 'X = np.random.random(N)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        # 11
        statement, import_statement_lst = 'y1 = 0.2*x + np.random.rand(1000)', ['import numpy as np']
        fix_statement = return_fix_statement_for_random_statement(statement, import_statement_lst)
        print(statement, import_statement_lst, fix_statement)
        pass

if __name__ == '__main__':
    unittest.main()
