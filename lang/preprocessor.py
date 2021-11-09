#!/usr/bin/env python3

import re, sys, os
from pathlib import Path

def preprocessor(_code):
    new_code = _code
    for i, line in enumerate(new_code):
        for _regex in [r'import "(.*)"', r"import '(.*)'"]:
            for _import in re.findall(_regex, line):
                _path = os.path.join(os.getcwd(), _import)

                for _global_lib in re.findall(r'<(.*)>', _import):
                    _path = os.path.join(sys.path[0], 'libs', _global_lib)

                try:
                    with open(_path) as f:
                        contents = f.readlines()
                        codestart_line = contents.index("code_start;\n")
                        new_code[i] = ''.join(contents[codestart_line+1:])
                except FileNotFoundError as e:
                    print(f"The file '{_path}' doesn't seem to exist.")
                    sys.exit(2)
                except IsADirectoryError as e:
                    print(f"Looks like '{_path}' is a directory.")
                    sys.exit(2)
                except ValueError as e:
                    print(f"Hmm, 'code_start;' doesn't exist in '{_path}'.")
                    sys.exit(2)

    return new_code
