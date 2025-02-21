#!/usr/bin/python

print("""ATOM    499  CE  LYS    63      19.202  25.857    .891  1.00 23.42      1UBQ 569
ATOM    500  NZ  LYS    63      17.884  26.544   1.075  1.00 25.97      1UBQ 570
ATOM    501  N   GLU    64      22.099  29.163   5.605  1.00 10.04      1UBQ 571
ATOM    502  CA  GLU    64      21.907  30.563   5.881  1.00 10.94      1UBQ 572
ATOM    503  C   GLU    64      21.466  30.953   7.261  1.00  9.74      1UBQ 573
ATOM    504  O   GLU    64      21.066  32.112   7.533  1.00  9.42      1UBQ 574""")

print(''.join(str(i)*10 for i in range(8))[1:]+'8')
print(''.join(list(str(i) for i in range(10))*8)[1:]+'0')

print(\
"ATOM      1  Na      X   1       0.000   0.000   0.000  0.00  0.00          NA1+")
