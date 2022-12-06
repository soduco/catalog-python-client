"""
    helpers functions
"""

import os

def is_valid_file(parser, arg):
    """
        Test if file exist
    """

    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return open(arg, 'r', encoding='utf-8')  # return an open file handle
