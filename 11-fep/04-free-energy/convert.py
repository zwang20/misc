#!/usr/bin/python

# **attempts** to convert input files into files usable by namd
# because freesolv seems to support everything but

import parmed as pmd

gmx_top = pmd.load_file('mobley_9055303.top', xyz='mobley_9055303.gro')
gmx_top.save('methane_solvated.psf')
gmx_top.save('methane_solvated.pdb')

import re

# # TODO: dont use this stupid implementation
# def remove_extra_space(text):
#     """Removes extra ' 's from sequences with more than two ' 's.
#
#     Args:
#         text: The input string.
#
#     Returns:
#         The modified string.
#     """
#
#     def replace_func(match):
#         return match.group(0)[2:]
#
#     return re.sub(r"  +", replace_func, text)
#
# with open('output.psf') as input_file:
#     with open('converted.psf', 'w') as output_file:
#         for line in input_file:
#             output_file.write(remove_extra_space(line))
