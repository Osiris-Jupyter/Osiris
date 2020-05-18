import argparse, sys, os
import Osiris

parser = argparse.ArgumentParser(description='return python version of a notebook')
parser.add_argument('-n', '--name', type=str, required=True)
parser.add_argument('-e', '--execute', type=str, required=True)
args = parser.parse_args()

interface = Osiris.UserInterface(args.name, args.execute, verbose=False)
missing_packages = interface.return_missing_packages()
return_str = ''
for (idx, package) in enumerate(missing_packages):
    if idx is not 0:
        return_str+=','
    return_str += package
print(return_str)

