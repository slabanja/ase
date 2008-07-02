# -*- coding: utf-8 -*-
# creates:  diffusion-I.png  diffusion-T.png  diffusion-F.png diffusion-barrier.png
import os
from ase import *
from ase.neb import fit
if 1:
    execfile('diffusion1.py')
    execfile('diffusion2.py')
images = read('neb.traj@-5:')
for name, a in zip('ITF', images[::2]):
    cell = a.get_cell()
    a = a * (2, 2, 1)
    a.set_cell(cell)
    write('diffusion-%s.pov' % name, a, show_unit_cell=True, pause=False)
    os.system('povray diffusion-%s.ini' % name)
s, E, Sfit, Efit, lines = fit(images)
import pylab as plt
plt.figure(figsize=(4.5, 3))
plt.plot(s, E, 'o')
plt.plot(Sfit, Efit, 'k-')
for x, y in lines:
    plt.plot(x, y, 'g-')
plt.xlabel(u'path [Å]')
plt.ylabel(u'energy [eV]')
plt.title('Maximum: %.3f eV' % max(Efit))
plt.savefig('diffusion-barrier.png')