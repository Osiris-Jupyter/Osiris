import ast
import numpy as np
import json
from _ast import *
from .func_calls_visitor import get_func_calls
from .vars_visitor import get_vars
from copy import deepcopy
import queue

built_in_names = [ 
        "abs","delattr","hash","memoryview",
        "set","all", "dict", "help", "min",
        "setattr", "any", "dir", "hex", "next",
        "slice", "ascii", "divmod", "id", "object",
        "sorted", "bin", "enumerate", "input", "oct",
        "staticmethod", "bool", "eval", "int", "open",
        "str","breakpoint", "exec", "isinstance", "ord",
        "sum", "bytearray", "filter", "issubclass", "pow",
        "super", "bytes", "float", "iter", "print",
        "tuple", "callable", "format", "len", "property",
        "type", "chr", "frozenset", "list", "range",
        "vars", "classmethod", "getattr","locals", "repr",
        "zip", "compile", "globals", "map", "reversed",
        "__import__", "complex", "hasattr", "max","round",
        "__name__", 'ImportError', 'IPython','ValueError'
        ]

class FilterTransformer(ast.NodeTransformer):
    def __init__(self):
        self.class_names = []
    def visit_ClassDef(self, node):
        self.class_names += [node.name]
        return None
    def visit_AugAssign(self, node):
        target_tmp = deepcopy(node.target)
        target_tmp.ctx = ast.Load()
        tmp_node = ast.Assign(targets=[node.target],
                value=BinOp(left=target_tmp,
            op=node.op, right=node.value))
        return tmp_node

def get_fun_ref_id(tree):
    func_ref_ids = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) :
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None:
                    func_ref_ids += [d['name']]
                else:
                    func_ref_ids += [d['asname']]
        if isinstance(node, ast.ImportFrom):
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None:
                    func_ref_ids += [d['name']]
                else:
                    func_ref_ids += [d['asname']]
    return func_ref_ids

class CRG:

    def __init__(self):
        self.producer_list = []  # a list of producer list 
        self.consumer_list = []   # a list of consumer list
        self.adj_mat = None

    def update_symbol_table(self, node):
        transfomer = FilterTransformer()  # remove classes 
        node = transfomer.visit(node)
        func_records = get_func_calls(node)  # function calls (no object's  member included)
        vars_records = get_vars(node)        # variables / objects 
        func_ref_ids = get_fun_ref_id(node)  # from import names

        class_ref_ids = transfomer.class_names  # get class names
        func_records = [(tmp,'def') for tmp in class_ref_ids+func_ref_ids] + func_records # make sure defs are ahead of load
        vars_records = [(tmp, 'store') for tmp in class_ref_ids+func_ref_ids] + vars_records
        producer_set = set()
        consumer_set = set()
        for e in vars_records:
            if e[0] in built_in_names:
                continue
            if e[1]=='def' or e[1]=='store' and (e[0],'var') not in consumer_set:
                producer_set.add((e[0], 'var'))
            elif e[1]=='load':
                consumer_set.add((e[0], 'var'))

        for e in func_records:
            if e[0] in built_in_names:
                continue
            if e[1]=='def' or e[1]=='store':
                producer_set.add((e[0], 'fun'))
                producer_set.add((e[0], 'var'))
            elif e[1]=='load':
                consumer_set.add((e[0], 'fun'))

        self.producer_list += [producer_set]
        self.consumer_list  += [consumer_set]
    def build(self, code_list):
        self.N = len(code_list)
        mat = np.zeros((self.N, self.N))
        self.adj_mat = np.zeros((self.N, self.N), dtype=int)
        for idx, code in enumerate(code_list):
            #print(idx)
            #print(code)
            try:
                tree = ast.parse(code, mode='exec')
                self.update_symbol_table(tree)
            except(SyntaxError):
                tree = ast.parse("", mode='exec')
                self.update_symbol_table(tree)
                print('warning!! Synatx Error')
        return self.adj_mat

    def get_topological_order(self):
        self.build_adj_mat()
        adj_mat = deepcopy(self.adj_mat)
        exec_order = []
        n = adj_mat.shape[0]
        in_degrees = np.sum(self.adj_mat, axis=0)
        todo_node_idx = (in_degrees==0).nonzero()[0].tolist()# in-degree=0 
        while len(exec_order)<n:
            for i in todo_node_idx:
                if i not in exec_order:
                    exec_order += [i]
                    adj_mat[i] = np.zeros(n)
            in_degrees = np.sum(adj_mat, axis=0)
            todo_node_idx = (in_degrees==0).nonzero()[0].tolist()# in-degree=0

        return exec_order

    def all_topo_util(self,all_paths, res, visited, in_degrees):
        if len(all_paths)>=self.max_size:
            return 
        flag = False
        for i in range(self.N):
            if in_degrees[i] ==0 and visited[i]==False:
                adj_nodes = self.adj_mat[i].nonzero()[0].tolist()
                in_degrees[adj_nodes] = in_degrees[adj_nodes]-1
                res.append(i)
                visited[i] = True
                self.all_topo_util(all_paths, res, visited, in_degrees)
                # backtracking 
                visited[i] = False
                res.pop()
                in_degrees[adj_nodes] += 1
                flag = True
        if not flag:
            all_paths.append(deepcopy(res))

    def alltopologicalSort(self, all_paths):
        visited = [False]*self.N
        in_degrees = np.sum(self.adj_mat, axis=0)
        res = []
        self.all_topo_util(all_paths, res, visited, in_degrees)

    def all_topo_with_oec_util(self, all_paths, res, accum_producer_set):
        oec_tmp = [0]*self.N
        counter = 0
        for i in res:
            counter += 1
            oec_tmp[i] = counter
            if counter > self.oec[i]:
                return
        if len(res) >= self.max_oec:
            if oec_tmp == self.oec:
                all_paths.append(deepcopy(res))
            return

        for i in range(self.N):
                accum_producer_set_tmp = accum_producer_set.union(self.producer_list[i])
                if self.consumer_list[i].issubset(accum_producer_set_tmp):
                    accum_producer_set = accum_producer_set_tmp
                    res.append(i)
                    accum_producer_set_bk = deepcopy(accum_producer_set)  # to be checked
                    self.all_topo_with_oec_util(all_paths, res, accum_producer_set)
                    accum_producer_set = accum_producer_set_bk
                    res.pop()

    def all_topo_with_oec(self, all_paths, oec):
        in_degrees = np.sum(self.adj_mat, axis=0)
        res = []
        self.oec = oec
        self.max_oec = max(self.oec)
        oec_tmp = [0]*self.N
        counter = 0
        accum_producer_set = set()
        self.all_topo_with_oec_util(all_paths, res, accum_producer_set)

    def all_topo_util(self, all_paths, res, accum_producer_set, visited):
        flag = False
        if len(all_paths)>=self.max_size:
            return 
        for i in range(self.N):
            accum_producer_set_tmp = accum_producer_set.union(self.producer_list[i])
            if self.consumer_list[i].issubset(accum_producer_set_tmp) and visited[i]==False:
                accum_producer_set_bk = deepcopy(accum_producer_set)
                accum_producer_set = accum_producer_set_tmp
                res.append(i)
                visited[i]=True

                self.all_topo_util(all_paths, res, accum_producer_set, visited)
                accum_producer_set = accum_producer_set_bk
                res.pop()
                visited[i]=False
                flag = True
        if not flag:
            all_paths.append(deepcopy(res))


    def all_topo(self, all_paths, max_size=200):
        res = []
        visited = [False]*self.N
        accum_producer_set = set()
        self.max_size=max_size
        self.all_topo_util(all_paths, res, accum_producer_set, visited)

    def gen_exec_path(self, mode='single', oec=[]):
        if mode == 'single':
            all_paths = []
            self.all_topo(all_paths, max_size=1)
            exec_order = all_paths[0]
            return exec_order
        if mode == 'all':
            all_paths = []
            self.all_topo(all_paths)
            return all_paths
        if mode == 'oec':
            all_paths = []
            self.all_topo_with_oec(all_paths, oec)
            return all_paths
