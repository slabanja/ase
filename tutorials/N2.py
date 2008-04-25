from ase import *

atom = Atoms('N')
atom.set_calculator(EMT())
e_atom = atom.get_potential_energy()

d = 1.1
molecule = Atoms('2N', [(0., 0., 0.), (0., 0., d)])
molecule.set_calculator(EMT())
e_molecule = molecule.get_potential_energy()

e_atomization = e_molecule - 2 * e_atom

print 'Atomization energy:', - e_atomization, 'eV'