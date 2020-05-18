import ast

from .dependency_graph_utils import get_code_list
from .func_calls_visitor import get_func_calls

whitelist = {
        'numpy.random.*':'numpy.random.seed(100)',
        'sklearn.utils.random.*':'numpy.random.seed(100)',
        'random.*':'random.seed(100)',
        'scipy.sparse.random.*':'numpy.random.seed(100)'
        }

def match_api(func_call_name, api_name):
    func_call_parts = func_call_name.split('.')
    api_parts = api_name.split('.')
    m = len(func_call_parts)
    n = len(api_parts)
    idx = 0
    while idx < min(m, n):
        if api_parts[idx]=='*' or api_parts[idx] == func_call_parts[idx]:
            idx += 1
        else:
            return False
    return True

def match_whitelist(name):
    for api_name in whitelist.keys():
        if match_api(name, api_name):
            return whitelist[api_name]
    return None

def get_api_ref_id(tree):
    id2fullname  = {}  # key is the imported module while the value is the prefix
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) :
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None:
                    id2fullname[d['name']] = d['name']
                else:
                    id2fullname[d['asname']] = d['name']
        if isinstance(node, ast.ImportFrom):
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None:
                    id2fullname[d['name']] = node.module+'.'+d['name']
                else:
                    id2fullname[d['asname']] = node.module+'.'+d['name']
    return id2fullname

def func_call_format(func_call_names, id2fullname):
    result = []
    for name in func_call_names:
        name_parts = name.split('.')
        if name_parts[0] in id2fullname:
            full_name = id2fullname[name_parts[0]] + '.'+ ".".join(name_parts[1:])
            result += [full_name.rstrip('.')]
    return result

def detect(filename):
    code_list = get_code_list(filename)
    code = "\n".join(code_list)
    try:
        whole_tree = ast.parse(code)
    except (SyntaxError,):  # to avoid non-python code
        return (False, 'SyntaxError')
    id2fullname = get_api_ref_id(whole_tree)
    suspected_func_fullnames = set()
    required_call_names = set()
    for code in code_list:
        tree = ast.parse(code, mode='exec')
        cell_func_calls_names = get_func_calls(tree, extended=True)
        cell_func_calls_names = [tmp[0] for tmp in cell_func_calls_names]
        cell_func_calls_names = func_call_format(cell_func_calls_names, id2fullname)
        # all relevant function calls
        suspected_func_fullnames.update(cell_func_calls_names)
        for name in cell_func_calls_names:
            res = match_whitelist(name)
            if res is not None:
                required_call_names.add(res)
    for candidate in required_call_names:
        if candidate not in suspected_func_fullnames:
            return (False, 'inadvisable usage')
    return (True, 'ok')

def is_impeded(smt, import_smts):
    try:
        code = "\n".join(import_smts)
        import_smts_tree = ast.parse(code)
        id2fullname = get_api_ref_id(import_smts_tree)

        tree = ast.parse(smt)
        cell_func_calls_names = get_func_calls(tree, extended=True)
        cell_func_calls_names = [tmp[0] for tmp in cell_func_calls_names]
        cell_func_calls_names = func_call_format(cell_func_calls_names, id2fullname)

        if len(cell_func_calls_names) == 0:
            return False
        sol = match_whitelist(cell_func_calls_names[0])
        if sol is not None:
            return True
        return False

    except (SyntaxError,):  # to avoid non-python code
        return (False, 'SyntaxError')

def get_antidote(smt, import_smts):
    try:
        code = "\n".join(import_smts)
        import_smts_tree = ast.parse(code)
        id2fullname = get_api_ref_id(import_smts_tree)

        tree = ast.parse(smt.lstrip())
        cell_func_calls_names = get_func_calls(tree, extended=True)
        cell_func_calls_names = [tmp[0] for tmp in cell_func_calls_names]
        cell_func_calls_names = func_call_format(cell_func_calls_names, id2fullname)
 
        if len(cell_func_calls_names) == 0:
            return None
        sol = match_whitelist(cell_func_calls_names[0])
        return ["import {}".format(sol.split('.')[0]), sol]

    except (SyntaxError,):  # to avoid non-python code
        print('SyntaxError!!!!!!!!!!!!')
        return None

if __name__ == '__main__':
    print(0)

