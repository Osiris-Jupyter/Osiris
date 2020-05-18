# Osiris

Osiris is a tool for programmers to analyze Jupyter Notebooks before releases. We discovered that plentiful Jupyter Notebook files pushed on GitHub cannot reproduce anticipated outputs. Alternatively, even worse, some Jupyter Notebook files can even not be executed on different end devices.

Osiris aims to eliminate this problem. One can leverage Osiris to analyze their Jupyter Notebook files before releasement to the public, which can conclude potential reasons for causing non-reproducibility. By the assistance of Osiris, programmers can properly refine their Jupyter Notebook files and enhance reproducibility of Jupyter Notebook files. 

## Getting Started

These instructions will go through execution environments setup, usage, and unit tests for users to check functionalities of Osiris. 

### Prerequisites

Make sure both Conda (or Miniconda) and Pip installed. Install Conda via [the official website](https://www.anaconda.com/) or by pip. 

```
pip install conda 
```

### Setup 

Before the usage of Osiris, to cope with various python version and package requirements for Jupyter Notebook files. A setup.sh needs to be executed to deploy several Conda environments with several combinations between different versions python and ten selected packages. (Currently, Osiris has more than 200 packages pre-installed)

```
cd envs 
source ./setup.sh
```

Press yes during Conda environments installation if any. 
After executing setup.sh, Conda environments with 'Osiris_' prefix should be installed.
Execute the following command for verification. 

```
conda env list
```

display an image as a little demonstration 

### Running unit tests for Osiris 

To guarantee all functionalities of Osiris functions accurately. Please run unit tests by instructions below. These unit tests will analyze Jupyter notebook files stored in the tests folder to verify the correctness of Osiris in diverse circumstances. 

Note that for analyzing Jupyter Notebook files, Osiris requires some additional packages installed. For simplicity, activate the default environment of Osiris before running unit tests. 

```
conda activate Osiris_default
python3 test.py -b
```

## Benchbook 

```
conda activate Osiris_default
python3 benchbook_test.py -b
```

## Usage 

Follow instructions demonstrate how users can analyze their Jupyter Notebook files. To avoid unexpected failures, activate Osiris_default before leveraging Osiris. 

```
conda activate Osiris_default 
```

### Parameters 

For Osiris, there are several parameters for users to specify during usage. Below list out all parameters and the corresponding description. Please refer to the Terminology section for more illustration. 

- <b>notebook_path</b> (required) <br/>
  Please specify the relative path from runOsiris.sh. For instance, notebook.ipynb or folder/notebook.ipynb. 
  
- <b>execute</b> (required) <br/>
  <b>options: normal/OEC/dependency</b> <br/>
  Please specify the execute strategy for analyzing Jupyter Notebook files. <br/>
  Currently, Osiris has three execute strategies, including normal (top-to-down), OEC (original execution_count), and dependency. Each of them executes Jupyter Notebook files in different order. 
  
- <b>verbose</b> (optional) <br/>
  <b>Usage: -v</b> <br/>
  If False, Osiris will filter out all processing/debugging information, leaving only statistic results  — for instance, executability and reproducibility ratio. In contrast, if True, all processing/debugging information like the source code of non-reproducible cells will be listed out. 
  
- <b>match pattern</b> (optional) <br/>
  <b>Usage: -m pattern</b> <br/>
  <b>options: strong/weak/best_effort</b> <br/>
  Set this option to analyze reproducibility of Jupyter Notebook files. Osiris automatically executes and compares outputs of Jupyter Notebook files according to match pattern given. 
  
- <b>self reproducibility</b> (optional) <br/>
  <b>Usage: -s</b> <br/>
  Set this option as True to activate analyses on self-reproducibility of cells. Osiris will analyze whether cells in Jupyter Notebook files are self-reproducible or not. If a cell is self-reproducible, it indicates the status of variables is equivalent for executing a cell once or multiple times.  
  
- <b>all potential execution paths</b> (optional) <br/>
  <b>Usage: -a</b> <br/>
  Set this option as True to activate analyses on all potential execution paths according to the Cell-Dependency Graph. Osiris will analyze each potential execution path individually and display corresponding analytical results. 
  
- <b>debug</b> (optional) <br/>
  <b>Usage: -d cell_index</b> <br/>
  <b>options: a valid number, where 0 indicates the first cell be executed</b> <br/>
  Set this option to analyze a specific cell in details for debugging purpose. Osiris will examine the status difference line by line and locate suspicious statement which may potentially induce the non-reproducibility.   
  

### Examples 

example 1: analyze whether a notebook is executable in normal (top-to-down) order

```
source ./runOsiris.sh target_notebook.ipynb normal 
```

example 2: analyze reproducibility of a given notebook, using strong match pattern, in OEC (original execution count) order

```
source ./runOsiris.sh target_notebook.ipynb OEC "-m strong"
```

example 3: analyze reproducibility of a given notebook, using strong match pattern, in OEC (original execution count) order with full information 

```
source ./runOsiris.sh target_notebook.ipynb OEC "-m strong -v"
```

example 4: analyze self-reproducibility of a given notebook in dependency order  

```
source ./runOsiris.sh target_notebook.ipynb dependency "-s"
```

example 5: analyze the first cell of a given notebook in normal (top-to-down) order, where Osiris will locate suspicious statement causing the status difference of variables. 

```
source ./runOsiris.sh target_notebook.ipynb normal "-d 0"
```

example 6: analyze both reproducibility of a given notebook, using strong match pattern, and self-reproducibility in OEC (original execution count) order with full information 

```
source ./runOsiris.sh target_notebook.ipynb OEC "-m strong -s -v"
```

## Terminology

- <b>Executable ratio</b><br/>
  The executable ratio refers to the ratio that the number of executable notebooks divided by the number of notebooks. Notice an executable notebook indicates Osiris can execute every cell in ascending Execution Count order, in which we do not consider partially executable notebooks as executable. 

- <b>OEC (Original Execution Count) Execution Strategy</b><br/>
  Original Execution Count indicates the Execution Count number associated with each cell. If a user specifies the Execution Strategy to be 'OEC', Osiris will execute and analyze notebooks in ascending Execution Count order. Notice that Osiris will exclude cells without Execution Count into consideration. 
  
- <b>Dependency Execution Strategy</b><br/>
  If a user specifies the Execution Strategy to be 'dependency', Osiris will execute the notebook according to the execution path given by Cell Dependency Graph. 
  
- <b>Reproducibility ratio</b><br/>
  Reproducibility ratio indicates that for a given notebook, the number of cells among all cells which can generate identical results (outputs) via re-execution of Osiris. Reproducibility ratio refers to the capability that a given notebook can reproduce identical results in various machines. 
  
- <b>Strong Match Pattern</b><br/>
  For measuring reproducibility ratio, if a user specifies Strong Match Pattern, Osiris will compare original output and output via re-execution for each cell. 
  
- <b>Weak Match Pattern</b><br/>
  For measuring reproducibility ratio, if a user specifies Weak Match Pattern, Osiris will execute two times individually and compare their outputs for each cell. 
  
- <b>Best Effort Match Pattern</b><br/>
  
- <b>Self-reproducibilty ratio</b><br/>
  For analyses, it would be beneficial for us to distinguish cells, which will have an identical effect on re-execution no matters how many times a particular cell is re-executed. It implies that all status (values) of self-defined variables will remain identical if we re-execute a particular cell more than once. 
  
- <b>What is debug in Osiris actually doing?</b><br/>
  For analyses, it would be beneficial for us to highlight suspicious statement which may cause the status difference of self-defined variables in a particular cell. If a user activates debug functionality, Osiris will inspect status line by line and locate suspicious statement for users. 
  
- <b>Cell Dependency Graph</b><br/>
The cell dependency graph depicts relations between different cells. Cell c1 is dependent on cell c2 if there exists at least one variable/object/function call, imported module usages appears in cell1 however defined, declared, reassigned, imported in cell 2. 


- <b>Algorithm behind execution paths generation for Dependency Execution Strategy</b><br/>
  The execution path is generated from the producer-consumer model with backtrace procedure. 
  
## Implementation Details 

- Before any re-execution and analyze, Osiris will preprocess the given Jupyter Notebook file, removing all markdown cells/raw cells/cells without Execution Count. 


## Acknowledgments

* Why it's called Osiris? <br/>
Osiris is the god of the afterlife, the underworld, and rebirth in ancient Egyptian religion. Our tool aims to enable Jupyter Notebook files to be executable, more reproducible, giving these files rebirth on different machines. That is the inspiration why I would like to name our tool as Jupyter Osiris. 
* More 
* etc

## Reference 

João Felipe Pimentel, Leonardo Murta, Vanessa Braganholo, and Juliana Freire. 1219 2019. A large-scale study about quality and reproducibility of jupyter notebooks. 1220 In Proceedings of the 16th International Conference on Mining Software Repositories. IEEE Press, 507–517.
