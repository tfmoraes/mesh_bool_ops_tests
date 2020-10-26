import sys
from pymeshfix import _meshfix

input_file = sys.argv[1]
output_file = sys.argv[2]

_meshfix.clean_from_file(input_file, output_file)
