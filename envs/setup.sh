#!/bin/bash

conda install conda=4.7.5
conda env create -f Osiris_py35.yml
conda env create -f Osiris_py36.yml
conda env create -f Osiris_py37.yml
conda env create -f Osiris_default.yml

conda activate Osiris_default 
pip install jupyter_client

conda install nb_conda nb_conda_kernels matplotlib
