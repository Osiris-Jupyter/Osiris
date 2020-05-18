import os 

import nbformat
import collections
import numpy as np

from .CRG import CRG
from .CRG import get_code_list, detect, get_antidote, get_path_by_extension, find_local_modules, get_oec

'''
The following utils functions are high-level usage of Jarix's implementation
'''
def distinguish_local_modules(import_statements):
    result = find_local_modules(import_statements)
    return result

def return_traverse_path(root_path):
    return get_path_by_extension(root_path)

def risk_detect(path):
    return detect(path)

def return_fix_statement_for_random_statement(statement, list_of_import_statements):
    return get_antidote(statement, list_of_import_statements)

def get_execution_order(path):
    code_list = get_code_list(path)
    graph = CDG()
    graph.build(code_list)
    path = graph.gen_exec_path(mode='single')
    return path 

def get_all_potential_execution_orders(path):
    code_list = get_code_list(path)
    oec = get_oec(path)
    graph = CDG()
    graph.build(code_list)
    paths = graph.gen_exec_path(mode='all', oec=oec)
    return paths

'''
This utils function, move_to_appropriate_location, aims to cope with relative path issue
'''
def move_to_appropriate_location(path):
    path_split_lst = path.split('/')
    # We need to cd to the same directory as the notebook
    if len(path_split_lst) > 1:
        cd_path_lst = path_split_lst[:-1]
        cd_path = '/'.join(cd_path_lst)
        os.chdir(cd_path)


'''
This utils function, store_nb, is just for debugging purpose
'''
def store_nb(nb, relative_path):
    with open(relative_path, 'w') as f:
        nbformat.write(nb, f)


'''
Following utils functions with 'extract_' as prefix aim to parse Jupyter Notebook files and extract useful information for further analyses 
'''
def extract_outputs_based_on_normal_order(cells):
    outputs = []
    for cell in cells:
        if len(cell.outputs) > 0:
            thorough_output_for_the_cell = ''
            for output in cell.outputs:
                if 'text' in output.keys():
                    thorough_output_for_the_cell += output.text
                elif 'data' in output.keys():
                    image_data = output.data
                    if 'image/png' in image_data.keys():
                        thorough_output_for_the_cell += image_data['image/png']
                    elif 'text/plain' in image_data.keys():
                        thorough_output_for_the_cell += image_data['text/plain']
                    else:
                        pass
            outputs.append(thorough_output_for_the_cell)
        else:
            outputs.append('')

    return outputs

def extract_outputs_based_on_OEC_order(cells):
    outputs = []
    cells = cells.copy()

    execution_count_lst = [cell.execution_count for cell in cells]
    OEC = sorted(range(len(execution_count_lst)),
                    key=lambda k: execution_count_lst[k])
    parsed_nb_cells = [cells[idx] for idx in OEC]
    for cell in parsed_nb_cells:
        if len(cell.outputs) > 0:
            thorough_output_for_the_cell = ''
            for output in cell.outputs:
                if 'text' in output.keys():
                    thorough_output_for_the_cell += output.text
                elif 'data' in output.keys():
                    image_data = output.data
                    if 'image/png' in image_data.keys():
                        thorough_output_for_the_cell += image_data['image/png']
                    elif 'text/plain' in image_data.keys():
                        thorough_output_for_the_cell += image_data['text/plain']
                    else:
                        pass
            outputs.append(thorough_output_for_the_cell)
        else:
            outputs.append('')

    return outputs

def extract_outputs_based_on_dependency_order(cells, execution_order):
    outputs = []
    cells = cells.copy()

    parsed_nb_cells = [cells[idx] for idx in execution_order]
    for cell in parsed_nb_cells:
        if len(cell.outputs) > 0:
            thorough_output_for_the_cell = ''
            for output in cell.outputs:
                if 'text' in output.keys():
                    thorough_output_for_the_cell += output.text
                elif 'data' in output.keys():
                    image_data = output.data
                    if 'image/png' in image_data.keys():
                        thorough_output_for_the_cell += image_data['image/png']
                    elif 'text/plain' in image_data.keys():
                        thorough_output_for_the_cell += image_data['text/plain']
                    else:
                        pass
            outputs.append(thorough_output_for_the_cell)
        else:
            outputs.append('')

    return outputs


def extract_source_code_from_unmatched_cells(cells, index_lst):
    cells = cells.copy()

    execution_count_lst = [cell.execution_count for cell in cells]
    OEC = sorted(range(len(execution_count_lst)),
                 key=lambda k: execution_count_lst[k])
    parsed_nb_cells = [cells[idx] for idx in OEC]

    unmatched_cells = [cell for (idx, cell) in enumerate(
        parsed_nb_cells) if idx in index_lst]
    unmatched_cells = unmatched_cells.copy()
    source_code_of_unmatched_cells = [
        cell['source'] for cell in unmatched_cells]

    return source_code_of_unmatched_cells


'''
All remaining utils functions below are for printing purpose (PENDING)
'''
def print_source_code_of_unmatched_cells(cells, analyse_strategy, index_lst, unmatched_original_outputs, unmtached_executed_outputs, execution_order=None):
    cells = cells.copy()

    if analyse_strategy == 'normal':
        parsed_nb_cells = cells
    elif analyse_strategy == 'OEC':
        execution_count_lst = [cell.execution_count for cell in cells]
        OEC = sorted(range(len(execution_count_lst)), key=lambda k: execution_count_lst[k])
        parsed_nb_cells = [cells[idx] for idx in OEC]
    elif analyse_strategy == 'dependency':
        parsed_nb_cells = [cells[idx] for idx in execution_order]
    
    unmatched_cells = [cell for (idx, cell) in enumerate(parsed_nb_cells) if idx in index_lst]
    unmatched_cells = unmatched_cells.copy() # in case we would modify any content

    for (cell_idx, cell, original_output, executed_output) in zip(index_lst, unmatched_cells, unmatched_original_outputs, unmtached_executed_outputs):
        if 'source' in cell.keys():
            print('-------------------------------------------')
            print('Source Code of a Unmatched Cell', cell_idx)
            print('-------------------------------------------')
            print(cell['source'])

            print()
            print('-----------------')
            print('Original output:')
            print(original_output)
            print('Executed output:')
            print(executed_output)


