#!/bin/bash/

# Parse parameters from runOsiris.sh to analyse_nb.py
if [ -z "$1" ]
then 
    echo "\$1 is empty. Please indicate proper path to the target Jupyter Notebook file"
    return 
fi 

if [ -z "$2" ]
then 
    echo "$2 is empty. Please indicate one of valid execute strategies (normal/OEC/dependency)"
    return
fi 

# Grab the python version 
py_version=$(python3 grab_py_version.py -n "$1" -e $2)
echo $py_version

# Switch to appropriate conda environment 
if [ "$py_version" = "3.5" ]
then 
    conda activate Osiris_py35
elif [ "$py_version" = "3.6" ]
then
    conda activate Osiris_py36 
elif [ "$py_version" = "3.7" ]
then
    conda activate Osiris_py37 
elif [ "$py_version" = "2.7" ]
then
    # conda activate Osiris_py27
    return  
elif [ "$py_version" = "3.4" ]
then
    conda activate Osiris_py34
else 
    echo "$py_version"
    return 
fi 

# This part should be enable for users to utilzie Osiris but not in experiments 
# Grab the missing packages 
: '
missing_packages=$(python3 grab_missing_packages.py -n "$1" -e $2)
'

# This part should be enable for users to utilzie Osiris but not in experiments 
# Install the missing packages
: '
Field_Separator=$IFS
IFS=,
for package in $missing_packages; do	
	conda install $package
done
			
IFS=$Field_Separator
'

# Run Osiris  
python3 analyse_nb.py -n "$1" -e $2 $3

# exit conda env before leaving shell script 
conda deactivate 


