# creates: a1.png a2.png a3.png
from ase import *
atoms = Atoms([Atom('Ni', (0, 0, 0)),
               Atom('Ni', (0.45, 0, 0)),
               Atom('Ni', (0, 0.5, 0)),
               Atom('Ni', (0.5, 0.5, 0))])
atoms[1].x = 0.5
from math import sqrt
a=3.55
cell=[(2/sqrt(2.)*a, 0, 0),
      (1/sqrt(2.)*a, sqrt(3./2.)*a, 0),
      (0, 0, 10*sqrt(3.)/3.*a)]
atoms.set_cell(cell,fix=False)
write('a1.png', atoms, rotation='-73x', show_unit_cell=True)
a = atoms.repeat((3, 3, 2))
a.set_cell(atoms.get_cell(), fix=True)
write('a2.png', a, rotation='-73x', show_unit_cell=True)
xyzcell=identity(3) # The 3x3 unit matrix
atoms.set_cell(xyzcell, fix=False)  # Set the unit cell and rescale
atoms.append(Atom('Ni', (1/6., 1/6., .1)))  
atoms.set_cell(cell, fix=False)  # Set the unit cell and scale back
a = atoms.repeat((3, 3, 1))
a.set_cell(atoms.get_cell(), fix=True)
write('a3.png', a, show_unit_cell=True)