import csv, argparse, sys
from threading import Thread

sys.path.append('/home/dabao/Osiris')
import Osiris

ROOT_FOR_TESTS = '/home/dabao/Osiris/tests'
# ROOT_FOR_TESTS = 'C://Users//User//Desktop//Osiris//tests//'

def massive_notebooks_analyze(start_idx, end_idx):
    csv_file = open('downloaded_notebooks.csv', 'r', encoding='utf-8')
    reader = csv.reader(csv_file) 

    csv_file_storage = open('records.csv', 'a')
    writer = csv.writer(csv_file_storage)

    for row_idx, row in enumerate(reader):
        nb_idx = row_idx + 1
        if nb_idx >= start_idx and nb_idx <= end_idx:
            original_repo_path, notebook_path = row[0], row[1]
            original_repo_path_lst = original_repo_path.split('/')
            folder_path = original_repo_path_lst[0]+'@'+original_repo_path_lst[1]

            path = '/mnt/fit-Knowledgezoo/jupyternotebooks/'+folder_path+'/'+notebook_path
            
            try:
                print('--------------------------------------------------')
                print(nb_idx, path)
                print('--------------------------------------------------')
                interface = Osiris.UserInterface(path)
                for analyze_strategy in ['normal', 'OEC']:
                # for analyze_strategy in ['dependency']:
                    row = []
                    row.append(nb_idx)
                    row.append(analyze_strategy)
                    # print('DEBUG POINT:', row)
                    verbose = False 
                    print(analyze_strategy)
                    
                    is_executable = interface.analyse_executability(verbose=verbose, store=False, analyze_strategy=analyze_strategy)
                    print('Executability:', is_executable)
                    row.append(is_executable)
                    # print('DEBUG POINT:', row)
                    
                    num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_outputs(verbose=verbose, store=False, analyze_strategy=analyze_strategy, strong_match=True)
                    print('Mathcing ratio (strong):', match_ratio)
                    row.append(match_ratio)
                    # print('DEBUG POINT:', row) 
                    
                    num_of_matched_cells, num_of_cells, match_ratio, matched_cell_idx, source_code_from_unmatched_cells = interface.analyse_outputs(verbose=verbose, store=False, analyze_strategy=analyze_strategy, strong_match=False)
                    print('Mathcing ratio (weak):', match_ratio)
                    row.append(match_ratio)
                    # print('DEBUG POINT:', row)
                   
                    '''
                    num_of_reproducible_cells, num_of_cells, reproducible_ratio, reproducible_cell_idx = interface.analyse_reproducibility(verbose=verbose, store=False, analyze_strategy=analyze_strategy)
                    print('Reproducible ratio:', reproducible_ratio)
                    row.append(reproducible_ratio)
                    print('DEBUG POINT:', row)
                    '''

                    writer.writerow(row)

                print()
            except Exception as e:
                print(e)

parser = argparse.ArgumentParser(
    description='analysize Jupyter Notebook files')
parser.add_argument('--start-index', type=int, required=True)
parser.add_argument('--end-index', type=int, required=True)
args = parser.parse_args()

massive_notebooks_analyze(args.start_index, args.end_index)

# Multithread
'''
num_of_notebooks_per_thread = 10
num_of_threads = 5
assert int(num_of_notebooks_per_thread*num_of_threads) == 50

threads = [Thread(target=auto_analysize, args=(int(i*num_of_notebooks_per_thread+1), int(i*num_of_notebooks_per_thread+10))) for i in range(num_of_threads)]

for i, t in enumerate(threads):
    time.sleep(1)
    print(i, 'th thread begins')
    t.start()

for t in threads:
    t.join()

print('main thread exits')
'''
