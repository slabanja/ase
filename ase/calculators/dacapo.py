import numpy as np

from ase.old import OldASEListOfAtomsWrapper

try:
    import Numeric as num
except ImportError:
    pass
    
def np2num(a, typecode=num.Float):
    if num.__version__ > '23.8':
        return num.array(a, typecode)
    b = num.fromstring(a.tostring(), typecode)
    b.shape = a.shape
    return b

def restart(filename, **kwargs):
    calc = Dacapo(filename, **kwargs)
    atoms = calc.get_atoms()
    return atoms, calc

class Dacapo:
    def __init__(self, filename=None, **kwargs):
        from Dacapo import Dacapo
        if filename is not None:
            self.loa = Dacapo.ReadAtoms(filename, **kwargs)
            self.calc = self.loa.GetCalculator()
        else:
            self.calc = Dacapo(**kwargs)
            self.loa = None
            
    def update(self, atoms):
        if self.loa is None:
            from ASE import Atom, ListOfAtoms
            numbers = atoms.get_atomic_numbers()
            positions = atoms.get_positions()
            magmoms = atoms.get_initial_magnetic_moments()
            self.loa = ListOfAtoms([Atom(Z=numbers[a],
                                         position=positions[a],
                                         magmom=magmoms[a])
                                    for a in range(len(atoms))],
                                   cell=np2num(atoms.get_cell()),
                                   periodic=tuple(atoms.get_pbc()))
            self.loa.SetCalculator(self.calc)
        else:
            self.loa.SetCartesianPositions(np2num(atoms.get_positions()))
            self.loa.SetUnitCell(np2num(atoms.get_cell()), fix=True)
            
    def get_atoms(self):
        return OldASEListOfAtomsWrapper(self.loa)
            
    def get_potential_energy(self, atoms):
        self.update(atoms)
        return self.calc.GetPotentialEnergy()

    def get_forces(self, atoms):
        self.update(atoms)
        return np.array(self.calc.GetCartesianForces())

    def get_stress(self, atoms):
        self.update(atoms)
        return np.array(self.calc.GetStress())

    def get_number_of_bands(self):
        return self.calc.GetNumberOfBands()

    def get_kpoint_weights(self):
        return np.array(self.calc.GetIBZKPointWeights())

    def get_number_of_spins(self):
        return 1 + int(self.calc.GetSpinPolarized())

    def get_eigenvalues(self, kpt=0, spin=0):
        return np.array(self.calc.GetEigenvalues(kpt, spin))

    def get_fermi_level(self):
        return self.calc.GetFermiLevel()

    def get_number_of_grid_points(self):
        return np.array(self.get_pseudo_wave_function(0, 0, 0).shape)

    def get_pseudo_density(self, s=0):
        return np.array(self.calc.GetDensityArray(s))
    
    def get_pseudo_wave_function(self, n=0, k=0, s=0, pad=True):
        kpt = self.get_bz_k_points()[k]
        state = self.calc.GetElectronicStates().GetState(band=n, spin=s,
                                                         kptindex=k)

        # Get wf, without bolch phase (Phase = True doesn't do anything!)
        wave = state.GetWavefunctionOnGrid(phase=False)

        # Add bloch phase if this is not the Gamma point
        if np.all(kpt == 0):
            return wave
        coord = state.GetCoordinates()
        phase = coord[0] * kpt[0] + coord[1] * kpt[1] + coord[2] * kpt[2]
        return np.array(wave) * np.exp(-2.j * np.pi * phase) # sign! XXX

        #return np.array(self.calc.GetWaveFunctionArray(n, k, s)) # No phase!

    def get_bz_k_points(self):
        return np.array(self.calc.GetBZKPoints())

    def get_ibz_k_points(self):
        return np.array(self.calc.GetIBZKPoints())

    def get_wannier_localization_matrix(self, nbands, dirG, kpoint,
                                        nextkpoint, G_I, spin):
        return np.array(self.calc.GetWannierLocalizationMatrix(
            G_I=G_I.tolist(), nbands=nbands, dirG=dirG.tolist(),
            kpoint=kpoint, nextkpoint=nextkpoint, spin=spin))
    
    def initial_wannier(self, initialwannier, kpointgrid, fixedstates,
                        edf, spin):
        # Use initial guess to determine U and C
        init = self.calc.InitialWannier(initialwannier, self.atoms,
                                        np2num(kpointgrid, num.Int))

        states = self.calc.GetElectronicStates()
        waves = [[state.GetWaveFunction()
                  for state in states.GetStatesKPoint(k, spin)]
                 for k in self.calc.GetIBZKPoints()] 

        init.SetupMMatrix(waves, self.calc.GetBZKPoints())
        c, U = init.GetListOfCoefficientsAndRotationMatrices(
            (self.calc.GetNumberOfBands(), fixedstates, edf))
        U = np.array(U)
        for k in range(len(c)):
            c[k] = np.array(c[k])
        return c, U
