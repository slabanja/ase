"""Berendsen NPT dynamics class."""

import numpy as np

#from ase.md import MolecularDynamics
from ase.md.nvtberendsen import NVTBerendsen
import ase.units as units
#import math


class NPTBerendsen(NVTBerendsen):
    """Berendsen (constant N, P, T) molecular dynamics.

    Usage: NPTBerendsen(atoms, timestep, temperature, taut, pressure, taup)

    atoms
        The list of atoms.
        
    timestep
        The time step.

    temperature
        The desired temperature, in Kelvin.

    taut
        Time constant for Berendsen temperature coupling.

    fixcm
        If True, the position and momentum of the center of mass is
        kept unperturbed.  Default: True.

    pressure
        The desired pressure, in bar (1 bar = 1e5 Pa).

    taup
        Time constant for Berendsen pressure coupling.

    compressibility
        The compressibility of the material, water 4.57E-5 bar-1, in bar-1

    """

    def __init__(self, atoms, timestep, temperature, taut=0.5e3*units.fs,
                 pressure = 1.01325, taup=1e3*units.fs,
                 compressibility=4.57e-5, fixcm=True,
                 trajectory=None, logfile=None, loginterval=1):

        NVTBerendsen.__init__(self, atoms, timestep, temperature, taut, fixcm,
                              trajectory, 
                              logfile, loginterval)
        self.taup = taup
        self.pressure = pressure
        self.compressibility = compressibility

    def set_taup(self, taut):
        self.taut = taut

    def get_taup(self):
        return self.taut

    def set_pressure(self, pressure):
        self.pressure = pressure

    def get_pressure(self):
        return self.pressure

    def set_compressibility(self, compressibility):
        self.compressibility = compressibility

    def get_compressibility(self):
        return self.compressibility

    def set_timestep(self, timestep):
        self.dt = timestep

    def get_timestep(self):
        return self.dt



    def scale_positions_and_cell(self):
        """ Do the Berendsen pressure coupling,
        scale the atom positon and the simulation cell."""

        taupscl = self.dt / self.taup
        stress = self.atoms.get_stress()
        old_pressure = self.atoms.get_isotropic_pressure(stress)
        scl_pressure = 1.0 - taupscl * self.compressibility / 3.0 * \
                       (self.pressure - old_pressure)

        #print "old_pressure", old_pressure
        #print "volume scaling by:", scl_pressure

        cell = self.atoms.get_cell()
        positions = self.atoms.get_positions()

        cell = scl_pressure * cell
        positions = scl_pressure * positions 

        self.atoms.set_cell(cell, scale_atoms=False)
        self.atoms.set_positions(positions)

        return 


    def step(self, f):
        """ move one timestep forward using Berenden NPT molecular dynamics."""

        NVTBerendsen.scale_velocities(self)
        self.scale_positions_and_cell()

        #one step velocity verlet
        atoms = self.atoms
        p = self.atoms.get_momenta()
        p += 0.5 * self.dt * f

        if self.fixcm:
            # calculate the center of mass
            # momentum and subtract it
            psum = p.sum(axis=0) / float(len(p))
            p = p - psum

        self.atoms.set_positions(self.atoms.get_positions() +
             self.dt * p / self.atoms.get_masses()[:,np.newaxis])

        # We need to store the momenta on the atoms before calculating
        # the forces, as in a parallel Asap calculation atoms may
        # migrate during force calculations, and the momenta need to
        # migrate along with the atoms.  For the same reason, we
        # cannot use self.masses in the line above.

        self.atoms.set_momenta(p)
        f = self.atoms.get_forces()
        atoms.set_momenta(self.atoms.get_momenta() + 0.5 * self.dt * f)


        return f
