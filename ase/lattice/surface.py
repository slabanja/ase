"""Helper functions for creating the most common surfaces and related tasks.

The helper functions can create the most common low-index surfaces,
add vacuum layers and add adsorbates.

"""

from ase.lattice.cubic import FaceCenteredCubic
from ase.lattice.hexagonal import HexagonalClosedPacked
import numpy as np
import ase

def fcc001(symbol, size=(1,1,1), latticeconstant=None, orthogonal=False):
    """FCC(001) surface with <110> directions along the x and y axes.

    Supported special adsorption sites: 'ontop', 'bridge' and 'hollow'.

    If the optional parameter `orthogonal` is true, an orthogonal
    unit cell containing two atoms is produced, otherwise a smaller
    one-atom unit cell with a tilted z-axis is produced.
    """
    if orthogonal:
        a = FaceCenteredCubic(directions=[[1,-1,0], [1,1,0],[0,0,1]], size=size,
                              symbol=symbol, latticeconstant=latticeconstant)
    else:
        a = FaceCenteredCubic(directions=[[1,-1,0], [1,1,0],[1,0,1]], size=size,
                              symbol=symbol, latticeconstant=latticeconstant)
    a._addsorbate_info = {'ontop': (0.5,0.5),
                          'bridge': (1.0,0.5), 'hollow': (1.0,1.0)}
    return a
        

def fcc111(symbol, size=(1,1,1), latticeconstant=None, orthogonal=False):
    """FCC(111) surface.

    Supported special adsorption sites: 'ontop', 'bridge', 'fcc' and 'hcp'.

    If the optional parameter `orthogonal` is true, an orthogonal unit
    cell containing six atoms is produced with <110> and <112>
    directions along the x and y axes.

    If the optional parameter `orthogonal` is false (the default), a
    unit cell containing one atom is produced, with <110> directions
    along all three axes.
    """
    if orthogonal:
        a = FaceCenteredCubic(directions=[[1,-1,0],[1,1,-2], [1,1,1]],
                              size=size, symbol=symbol,
                              latticeconstant=latticeconstant)
        a._addsorbate_info = {'ontop': (1.0/2, 1.0/6),
                              'bridge': (1.0/4, 5.0/12), 'fcc': (1/2.0, 1/2.0),
                              'hcp': (0, 1/3.0)}
        return a
    else:
        a = FaceCenteredCubic(directions=[[0,1,1],[1,0,1], [1,1,0]],
                              size=size, symbol=symbol,
                              latticeconstant=latticeconstant)
        offset = (size[2]-1) / 3.0
        a._addsorbate_info = {'ontop': (0.0 + offset, 0.0 + offset),
                              'bridge': (1.0/2 + offset, 1.0/2 + offset),
                              'fcc': (1.0/3 + offset, 1.0/3 + offset),
                              'hcp': (2.0/3 + offset, 2.0/3 + offset)}
        return a

def fcc110(symbol, size=(1,1,1), latticeconstant=None):
    """FCC(110) surface with <110> and <001> directions along the x and y axes.

    Supported special adsorption sites: 'ontop', 'shortbridge' and
    'longbridge'.

    The unit cell contains two atoms.
    """
    a = FaceCenteredCubic(directions=[[-1,1,0],[0,0,1], [1,1,0]], size=size,
                          symbol=symbol, latticeconstant=latticeconstant)
    a._addsorbate_info = {'ontop': (1.0/2, 1.0/2), 'shortbridge': (1, 1.0/2), 
                          'longbridge': (1.0/2, 1)}
    return a

def hcp0001(symbol, size=(1,1,1), latticeconstant=None, orthogonal=False):
    """HCP(0001) surface.

    If the optional parameter `orthogonal` is true, an orthogonal unit
    cell containing six atoms is produced, with [2,-1,-1,0] and
    [0,1,-1,0] directions along the x and y axes.

    If the optional parameter `orthogonal` is false (the default), a
    unit cell containing two atoms is produced, [2,-1,-1,0] and
    [1,1,-2,0] directions along the x and y axes, and a [0001]
    direction along the z axis.

    Supported special adsorption sites: XXXX
    """
    if orthogonal:
        a = HexagonalClosedPacked(directions=[[2,-1,-1,0], [0,1,-1,0],
                                              [0,0,0,1]],
                                  size=size, symbol=symbol,
                                  latticeconstant=latticeconstant)
    else:
        a = HexagonalClosedPacked(directions=[[2,-1,-1,0], [1,1,-2,0],
                                              [0,0,0,1]],
                                  size=size, symbol=symbol,
                                  latticeconstant=latticeconstant)
    a._addsorbate_info = {}
    return a


def add_vacuum(atoms, vacuum):
    """Add vacuum layer to the atoms.

    Parameters:

    atoms: An Atoms object most likely created by one of the
    ase.lattice modules.

    vacuum: The thickness of the vacuum layer (in Angstrom).
    """
    uc = atoms.get_cell()
    normal = np.cross(uc[0],uc[1])
    costheta = np.dot(normal, uc[2]) / np.sqrt(np.dot(normal,normal) *
                                               np.dot(uc[2],uc[2]))
    length = np.sqrt(np.dot(uc[2],uc[2]))
    newlength = length + vacuum/costheta
    uc[2] *= newlength/length
    atoms.set_cell(uc, fix=True)

def add_adsorbate(atoms, adsorbate, height, position, offset=None):
    """Add an adsorbate to a surface.

    This function adds an adsorbate to a slab.  If the slab is
    produced by one of the utility functions in ase.lattice.setup, it
    is possible to specify the position of the adsorbate by a keyword
    (the supported keywords depend on which function was used to
    create the atoms).

    If the adsorbate is a molecule, the first atom (number 0) is
    adsorbed to the surface, and it is the responsability of the user
    to orient the adsorbate in a sensible way.

    This function can be called multiple times to add more than one
    adsorbate.

    Parameters:

    atoms: The surface onto which the adsorbate should be added.

    adsorbate:  The adsorbate. Must be one of the following three types:
        A string containing the chemical symbol for a single atom.
        An atom object.
        An atoms object (for a molecular adsorbate).

    height: Height above the surface.

    position: The x-y position of the adsorbate, either as a tuple of
        two numbers or as a keyword (if the surface is produced by one
        of the functions in ase.lattice.surfaces).

    offset (default: None): Offsets the adsorbate by a number of unit
        cells. Mostly useful when adding more than one adsorbate.

    Note that position is given in absolute xy coordinates (or as a
    keyword), whereas offset is specified in unit cells.  This can be
    used to give the positions in units of the unit cell by specifying
    position=(0,0) and using the offset instead.
    
    """
    if isinstance(position, type("string")):
        # A keyword
        try:
            info = atoms._addsorbate_info
        except AttributeError:
            raise TypeError, "If the atoms are not made by an ase.lattice.surface function, the position cannot be a keyword."
        try:
            pos = info[position]
        except KeyError:
            raise TypeError, "Adsorption site "+position+" not supported."
        size = atoms._addsorbate_info_size
        position = np.array(pos)/size
    else:
        position = np.array(position)

    if offset is not None:
        position += np.array(offset, np.float) / atoms._addsorbate_info_size
        
    # Get the surface z-coordinate.  Must use a stored value if an
    # adsorbate has already been added by a previous call to this
    # function.
    try:
        surfz = atoms._surfaceposition
    except AttributeError:
        surfz = max(atoms.get_positions()[:,2])
        atoms._surfaceposition = surfz
    adsorbtionsite = np.dot(np.array([position[0], position[1], 0]),
                            atoms.get_cell())
    adsorbtionsite[2] = surfz+height

    # Convert the adsorbate to an Atoms object
    if isinstance(adsorbate, ase.Atoms):
        ads = adsorbate
    elif isinstance(adsorbate, ase.Atom):
        ads = ase.Atoms(symbols=[adsorbate])
    else:
        # Hope it is a useful string or something like that
        ads = ase.Atoms(symbols=adsorbate, positions=np.array([[0.0,0.0,0.0]]))

    # Move adsorbate into position
    translation = adsorbtionsite - ads.get_positions()[0]
    ads.set_positions(translation + ads.get_positions())

    # Attach the adsorbate
    atoms.extend(ads)
    

                
                    
    