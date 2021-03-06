# husk:
# Exit*2?  remove pylab.show()
# close button
# DFT
# ADOS
# grey-out stuff after one second: vmd, rasmol, ...
# Show with ....
# rasmol: set same rotation as ag
# Graphs: save, Python, 3D
# start from python (interactive mode?)
# ascii-art option (colored)|
# option -o (output) and -f (force overwrite)
# surfacebuilder
# screen-dump
# icon
# ag-community-server
# translate option: record all translations, 
# and check for missing translations.

#TODO: Add possible way of choosing orinetations. \
#TODO: Two atoms defines a direction, three atoms their normal does
#TODO: Align orientations chosen in Rot_selected v unselcted
#TODO: Get the atoms_rotate_0 thing string
#TODO: Use set atoms instead og the get atoms
#TODO: Arrow keys will decide how the orientation changes
#TODO: Undo redo que should be implemented
#TODO: Update should have possibility to change positions
#TODO: Window for rotation modes and move moves which can be chosen
#TODO: WHen rotate and move / hide the movie menu

import os
import sys
import weakref
import numpy as np

import gtk
from ase.gui.view import View
from ase.gui.status import Status
from ase.gui.widgets import pack, help, Help, oops
from ase.gui.languages import translate as _

from ase.gui.settings import Settings
from ase.gui.surfaceslab import SetupSurfaceSlab
from ase.gui.nanoparticle import SetupNanoparticle
from ase.gui.nanotube import SetupNanotube
from ase.gui.graphene import SetupGraphene
from ase.gui.calculator import SetCalculator
from ase.gui.energyforces import EnergyForces
from ase.gui.minimize import Minimize
from ase.gui.scaling import HomogeneousDeformation
from ase.gui.quickinfo import QuickInfo
from ase.gui.defaults import read_defaults

ui_info = """\
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='Open'/>
      <menuitem action='New'/>
      <menuitem action='Save'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='EditMenu'>
      <menuitem action='SelectAll'/>
      <menuitem action='Invert'/>
      <menuitem action='SelectConstrained'/>
      <separator/>
      <menuitem action='Modify'/>
      <menuitem action='AddAtoms'/>
      <menuitem action='DeleteAtoms'/>
      <separator/>      
      <menuitem action='First'/>
      <menuitem action='Previous'/>
      <menuitem action='Next'/>
      <menuitem action='Last'/>
    </menu>
    <menu action='ViewMenu'>
      <menuitem action='ShowUnitCell'/>
      <menuitem action='ShowAxes'/>
      <menuitem action='ShowBonds'/>
      <separator/>
      <menuitem action='QuickInfo'/>
      <menuitem action='Repeat'/>
      <menuitem action='Rotate'/>
      <menuitem action='Colors'/>
      <menuitem action='Focus'/>
      <menuitem action='ZoomIn'/>
      <menuitem action='ZoomOut'/>
      <menuitem action='ResetView'/>
      <menuitem action='Settings'/>
      <menuitem action='VMD'/>
      <menuitem action='RasMol'/>
      <menuitem action='XMakeMol'/>
      <menuitem action='Avogadro'/>
    </menu>
    <menu action='ToolsMenu'>
      <menuitem action='Graphs'/>
      <menuitem action='Movie'/>
      <menuitem action='EModify'/>
      <menuitem action='Constraints'/>
      <menuitem action='RenderScene'/>
      <menuitem action='MoveAtoms'/>
      <menuitem action='RotateAtoms'/>
      <menuitem action='OrientAtoms'/>
      <menuitem action='DFT'/>
      <menuitem action='NEB'/>
      <menuitem action='BulkModulus'/>
    </menu>
    <menu action='SetupMenu'>
      <menuitem action='Surface'/>
      <menuitem action='Nanoparticle'/>
      <menuitem action='Graphene'/>
      <menuitem action='Nanotube'/>
    </menu>
    <menu action='CalculateMenu'>
      <menuitem action='SetCalculator'/>
      <separator/>
      <menuitem action='EnergyForces'/>
      <menuitem action='Minimize'/>
      <menuitem action='Scaling'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
      <menuitem action='Webpage'/>
      <menuitem action='Debug'/>
    </menu>
  </menubar>
</ui>"""

class GUI(View, Status):
    def __init__(self, images, rotations='', show_unit_cell=True,
                 show_bonds=False):
        self.images = images
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #self.window.set_icon(gtk.gdk.pixbuf_new_from_file('guiase.png'))
        self.window.set_position(gtk.WIN_POS_CENTER)
        #self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.connect('delete_event', self.exit)
        vbox = gtk.VBox()
        self.window.add(vbox)
        if gtk.pygtk_version < (2, 12):
            self.set_tip = gtk.Tooltips().set_tip

        actions = gtk.ActionGroup("Actions")
        actions.add_actions([
            ('FileMenu', None, '_File'),
            ('EditMenu', None, '_Edit'),
            ('ViewMenu', None, '_View'  ),
            ('ToolsMenu', None, '_Tools'),
            ('SetupMenu', None, '_Setup'),
            ('CalculateMenu', None, '_Calculate'),
            ('HelpMenu', None, '_Help'),
            ('Open', gtk.STOCK_OPEN, '_Open', '<control>O',
             'Create a new file',
             self.open),
             ('New', gtk.STOCK_NEW, '_New', '<control>N',
             'New ase.gui window',
             lambda widget: os.system('ag &')),
            ('Save', gtk.STOCK_SAVE, '_Save', '<control>S',
             'Save current file',
             self.save),
            ('Quit', gtk.STOCK_QUIT, '_Quit', '<control>Q',
             'Quit',
             self.exit),
            ('SelectAll', None, 'Select _all', None,
             '',
             self.select_all),
            ('Invert', None, '_Invert selection', None,
             '',
             self.invert_selection),
            ('SelectConstrained', None, 'Select _constrained atoms', None,
             '',
             self.select_constrained_atoms),
             ('Modify', None, '_Modify', '<control>Y',
              'Change tags, moments and atom types of the selected atoms',
              self.modify_atoms),
             ('AddAtoms', None, '_Add atoms', '<control>A',
              'Insert or import atoms and molecules',
              self.add_atoms),
             ('DeleteAtoms', None, '_Delete selected atoms', 'BackSpace',
              'Deletes the selected atoms',
              self.delete_selected_atoms),             
            ('First', gtk.STOCK_GOTO_FIRST, '_First image', 'Home',
             '',
             self.step),
            ('Previous', gtk.STOCK_GO_BACK, '_Previous image', 'Page_Up',
             '',
             self.step),
            ('Next', gtk.STOCK_GO_FORWARD, '_Next image', 'Page_Down',
             '',
             self.step),
            ('Last', gtk.STOCK_GOTO_LAST, '_Last image', 'End',
             '',
             self.step),
            ('QuickInfo', None, 'Quick Info ...', None,
             '',
             self.quick_info_window),
            ('Repeat', None, 'Repeat ...', None,
             '',
             self.repeat_window),
            ('Rotate', None, 'Rotate ...', None,
             '',
             self.rotate_window),
            ('Colors', None, 'Colors ...', None, '',
             self.colors_window),
            ('Focus', gtk.STOCK_ZOOM_FIT, 'Focus', 'F',
             '',
             self.focus),
            ('ZoomIn', gtk.STOCK_ZOOM_IN, 'Zoom in', 'plus',
             '',
             self.zoom),
            ('ZoomOut', gtk.STOCK_ZOOM_OUT, 'Zoom out', 'minus',
             '',
             self.zoom),
            ('ResetView', None, 'Reset View', 'equal',
             '',
             self.reset_view),
            ('Settings', gtk.STOCK_PREFERENCES, 'Settings ...', None,
             '',
             self.settings),
            ('VMD', None, 'VMD', None,
             '',
             self.external_viewer),
            ('RasMol', None, 'RasMol', None,
             '',
             self.external_viewer),
            ('XMakeMol', None, 'xmakemol', None,
             '',
             self.external_viewer),
            ('Avogadro', None, 'avogadro', None,
             '',
             self.external_viewer),
            ('Graphs', None, 'Graphs ...', None,
             '',
             self.plot_graphs),
            ('Movie', None, 'Movie ...', None,
             '',
             self.movie),
            ('EModify', None, 'Expert mode ...', '<control>E',
             '',
             self.execute),
            ('Constraints', None, 'Constraints ...', None,
             '',
             self.constraints_window),
            ('RenderScene', None, 'Render scene ...', None,
             '',
             self.render_window),
            ('DFT', None, 'DFT ...', None,
             '',
             self.dft_window),
            ('NEB', None, 'NE_B', None,
             '',
             self.NEB),
            ('BulkModulus', None, 'B_ulk Modulus', None,
             '',
             self.bulk_modulus),
            ('Bulk', None, '_Bulk Crystal', None,
             "Create a bulk crystal with arbitrary orientation",
             self.bulk_window),
            ('Surface', None, '_Surface slab', None,
             "Create the most common surfaces",
             self.surface_window),
            ('Nanoparticle', None, '_Nanoparticle', None,
             "Create a crystalline nanoparticle",
             self.nanoparticle_window),
            ('Nanotube', None, 'Nano_tube', None,
             "Create a nanotube",
             self.nanotube_window),
            ('Graphene', None, 'Graphene', None,
             "Create a graphene sheet or nanoribbon",
             self.graphene_window),
            ('SetCalculator', None, 'Set _Calculator', None,
             "Set a calculator used in all calculation modules",
             self.calculator_window),
            ('EnergyForces', None, '_Energy and Forces', None,
             "Calculate energy and forces",
             self.energy_window),
            ('Minimize', None, 'Energy _Minimization', None,
             "Minimize the energy",
             self.energy_minimize_window),
            ('Scaling', None, 'Scale system', None,
             "Deform system by scaling it",
             self.scaling_window),
            ('About', None, '_About', None,
             None,
             self.about),
            ('Webpage', gtk.STOCK_HELP, 'Webpage ...', None, None, webpage),
            ('Debug', None, 'Debug ...', None, None, self.debug)])
        actions.add_toggle_actions([
            ('ShowUnitCell', None, 'Show _unit cell', '<control>U',
             'Bold',
             self.toggle_show_unit_cell,
             show_unit_cell > 0),
            ('ShowAxes', None, 'Show _axes', None,
             'Bold',
             self.toggle_show_axes,
             True),
            ('ShowBonds', None, 'Show _bonds', '<control>B',
             'Bold',
             self.toggle_show_bonds,
             show_bonds),
            ('MoveAtoms', None, '_Move atoms', '<control>M',
             'Bold',
             self.toggle_move_mode,
             False),
            ('RotateAtoms', None, '_Rotate atoms', '<control>R',
             'Bold',
             self.toggle_rotate_mode,
             False),
            ('OrientAtoms', None, 'Orien_t atoms', '<control>T',
             'Bold',
             self.toggle_orient_mode,
             False)             
            ])
        self.ui = ui = gtk.UIManager()
        ui.insert_action_group(actions, 0)
        self.window.add_accel_group(ui.get_accel_group())

        try:
            mergeid = ui.add_ui_from_string(ui_info)
        except gobject.GError, msg:
            print 'building menus failed: %s' % msg

        vbox.pack_start(ui.get_widget('/MenuBar'), False, False, 0)
        
        View.__init__(self, vbox, rotations)
        Status.__init__(self, vbox)
        vbox.show()
        #self.window.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.connect('key-press-event', self.scroll)
        self.window.connect('scroll_event', self.scroll_event)
        self.window.show()
        self.graphs = []       # List of open pylab windows
        self.graph_wref = []   # List of weakrefs to Graph objects
        self.movie_window = None
        self.vulnerable_windows = []
        self.simulation = {}   # Used by modules on Calculate menu.
        self.module_state = {} # Used by modules to store their state.
        self.config = read_defaults()

    def run(self, expr=None):
        self.set_colors()
        self.set_coordinates(self.images.nimages - 1, focus=True)

        if self.images.nimages > 1:
            self.movie()

        if expr is None and not np.isnan(self.images.E[0]):
            expr = self.config['gui_graphs_string']
            
        if expr is not None and expr != '' and self.images.nimages > 1:
            self.plot_graphs(expr=expr)

        gtk.main()
    
            
    def step(self, action):
        d = {'First': -10000000,
             'Previous': -1,
             'Next': 1,
             'Last': 10000000}[action.get_name()]
        i = max(0, min(self.images.nimages - 1, self.frame + d))
        self.set_frame(i)
        if self.movie_window is not None:
            self.movie_window.frame_number.value = i
            
    def _do_zoom(self, x):
        """Utility method for zooming"""
        self.scale *= x
        self.draw()
        
    def zoom(self, action):
        """Zoom in/out on keypress or clicking menu item"""
        x = {'ZoomIn': 1.2, 'ZoomOut':1 /1.2}[action.get_name()]
        self._do_zoom(x)

    def scroll_event(self, window, event):
        """Zoom in/out when using mouse wheel"""
        SHIFT = event.state == gtk.gdk.SHIFT_MASK
        x = 1.0
        if event.direction == gtk.gdk.SCROLL_UP:
            x = 1.0 + (1-SHIFT)*0.2 + SHIFT*0.01
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            x = 1.0 / (1.0 + (1-SHIFT)*0.2 + SHIFT*0.01)
        self._do_zoom(x)

    def settings(self, menuitem):
        Settings(self)
        
    def scroll(self, window, event):
        from copy import copy    
        CTRL = event.state == gtk.gdk.CONTROL_MASK
        SHIFT = event.state == gtk.gdk.SHIFT_MASK
        dxdydz = {gtk.keysyms.KP_Add: ('zoom', 1.0 + (1-SHIFT)*0.2 + SHIFT*0.01, 0),
                gtk.keysyms.KP_Subtract: ('zoom', 1 / (1.0 + (1-SHIFT)*0.2 + SHIFT*0.01), 0),
                gtk.keysyms.Up:    ( 0, +1 - CTRL, +CTRL),
                gtk.keysyms.Down:  ( 0, -1 + CTRL, -CTRL),
                gtk.keysyms.Right: (+1,  0, 0),
                gtk.keysyms.Left:  (-1,  0, 0)}.get(event.keyval, None)
        try:
            inch = chr(event.keyval)
        except:
            inch = None
            
        sel = []

        atom_move = self.ui.get_widget('/MenuBar/ToolsMenu/MoveAtoms'
                                    ).get_active()
        atom_rotate = self.ui.get_widget('/MenuBar/ToolsMenu/RotateAtoms'
                                      ).get_active()
        atom_orient = self.ui.get_widget('/MenuBar/ToolsMenu/OrientAtoms'
                                      ).get_active()
        if dxdydz is None:
            return
        dx, dy, dz = dxdydz
        if dx == 'zoom':
            self._do_zoom(dy)
            return

        d = self.scale * 0.1
        tvec = np.array([dx, dy, dz])

        dir_vec = np.dot(self.axes, tvec)
        if (atom_move):
            rotmat = self.axes
            s = 0.1
            if SHIFT: 
                s = 0.01
            add = s * dir_vec
            for i in range(len(self.R)):
                if self.atoms_to_rotate_0[i]: 
                    self.R[i] += add
                    for jx in range(self.images.nimages):
                        self.images.P[jx][i] += add
        elif atom_rotate:
            from rot_tools import rotate_about_vec, \
                                  rotate_vec
            sel = self.images.selected
            if sum(sel) == 0:
                sel = self.atoms_to_rotate_0
            nsel = sum(sel)
            # this is the first one to get instatiated
            if nsel != 2: 
                self.rot_vec = dir_vec
                
            change = False
            z_axis = np.dot(self.axes, np.array([0, 0, 1]))
            if self.atoms_to_rotate == None:
                change = True 
                self.z_axis_old = z_axis.copy()
                self.dx_change = [0, 0]
                self.atoms_to_rotate = self.atoms_to_rotate_0.copy()
                self.atoms_selected = sel.copy()
                self.rot_vec = dir_vec
                    
            if nsel != 2 or sum(self.atoms_to_rotate) == 2:
                self.dx_change = [0, 0]
                
            for i in range(len(sel)):
                if sel[i] != self.atoms_selected[i]: 
                    change = True
            cz = [dx, dy+dz]      
            
            if cz[0] or cz[1]: 
                change = False
            if not(cz[0] * (self.dx_change[1])):
                change = True 
            for i in range(2):
                if cz[i] and self.dx_change[i]:
                    self.rot_vec = self.rot_vec * cz[i] * self.dx_change[i]
                    if cz[1]:
                        change = False
                
            if np.prod(self.z_axis_old != z_axis):
                change = True
            self.z_axis_old = z_axis.copy()           
            self.dx_change = copy(cz)
            dihedral_rotation = len(self.images.selected_ordered) == 4

            if change:
                self.atoms_selected = sel.copy()

                if nsel == 2 and sum(self.atoms_to_rotate) != 2:
                    asel = []
                    for i, j in enumerate(sel):
                        if j: 
                            asel.append(i)
                    a1, a2 = asel

                    rvx = self.images.P[self.frame][a1] - \
                          self.images.P[self.frame][a2]
                        
                    rvy = np.cross(rvx,
                                   np.dot(self.axes,
                                   np.array([0, 0, 1])))     
                    self.rot_vec = rvx * dx + rvy * (dy + dz)
                    self.dx_change = [dx, dy+dz]
                    
                # dihedral rotation?
                if dihedral_rotation:
                    sel = self.images.selected_ordered
                    self.rot_vec = (dx+dy+dz)*(self.R[sel[2]]-self.R[sel[1]])

            rot_cen = np.array([0.0, 0.0, 0.0])
            if dihedral_rotation:
                sel = self.images.selected_ordered
                rot_cen = self.R[sel[1]].copy()
            elif nsel: 
                for i, b in enumerate( sel):
                    if b: 
                        rot_cen += self.R[i]
                rot_cen /= float(nsel)     

            degrees = 5 * (1 - SHIFT) + SHIFT
            degrees = abs(sum(dxdydz)) * 3.1415 / 360.0 * degrees
            rotmat = rotate_about_vec(self.rot_vec, degrees)
            
            # now rotate the atoms that are to be rotated            
            for i in range(len(self.R)):
                if self.atoms_to_rotate[i]: 
                    self.R[i] -= rot_cen
                    for jx in range(self.images.nimages):
                        self.images.P[jx][i] -= rot_cen
                    
                    self.R[i] = rotate_vec(rotmat, self.R[i])
                    for jx in range(self.images.nimages):
                        self.images.P[jx][i] = rotate_vec(rotmat, self.images.P[jx][i])
                    
                    self.R[i] += rot_cen
                    for jx in range(self.images.nimages):
                        self.images.P[jx][i] += rot_cen
        elif atom_orient:
            to_vec  = np.array([dx, dy, dz])

            from rot_tools import rotate_vec_into_newvec
            rot_mat = rotate_vec_into_newvec(self.orient_normal, to_vec)
            self.axes = rot_mat
            
            self.set_coordinates()
        else:
            self.center -= (dx * 0.1 * self.axes[:, 0] -
                            dy * 0.1 * self.axes[:, 1])
        self.draw()
    
        
    def add_atoms(self, widget, data=None):
        """
        Presents a dialogbox to the user, that allows him to add atoms/molecule to the current slab.
        
        The molecule/atom is rotated using the current rotation of the coordinate system.
        
        The molecule/atom can be added at a specified position - if the keyword auto+Z is used,
        the COM of the selected atoms will be used as COM for the moleculed. The COM is furthermore
        translated Z ang towards the user.
        
        If no molecules are selected, the COM of all the atoms will be used for the x-y components of the
        active coordinate system, while the z-direction will be chosen from the nearest atom position 
        along this direction.
        
        Note: If this option is used, all frames except the active one are deleted.
        """
        if data:
            if data == 'load':
                chooser = gtk.FileChooserDialog(
                            _('Open ...'), None, gtk.FILE_CHOOSER_ACTION_OPEN,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
                ok = chooser.run()
                if ok == gtk.RESPONSE_OK:
                    filename = chooser.get_filename()
                chooser.destroy()
                if not ok:
                    return

            if data == 'OK' or data == 'load':
                import ase
                if data == 'load':
                    molecule = filename
                else:
                    molecule = self.add_entries[1].get_text()
                tag = self.add_entries[2].get_text()
                mom = self.add_entries[3].get_text()
                pos = self.add_entries[4].get_text().lower()

                a = None
                try:
                    a = ase.Atoms([ase.Atom(molecule)])
                except:      
                    try:
                        a = ase.data.molecules.molecule(molecule)
                    except:
                        try:
                            a = ase.io.read(molecule, -1)
                        except:
                            self.add_entries[1].set_text('?' + molecule) 
                            return ()
                        
                directions = np.transpose(self.axes)
                if a != None:
                    for i in a:
                        try: 
                            i.set_tag(int(tag))
                        except: 
                            self.add_entries[2].set_text('?' + tag) 
                            return ()
                        try: 
                            i.magmom = float(mom)
                        except: 
                            self.add_entries[3].set_text('?' + mom) 
                            return ()
                  # apply the current rotation matrix to A
                    for i in a:
                        i.position = np.dot(self.axes, i.position)       
                  # find the extent of the molecule in the local coordinate system
                    a_cen_pos = np.array([0.0, 0.0, 0.0])
                    m_cen_pos = 0.0
                    for i in a.positions:
                        a_cen_pos[0] += np.dot(directions[0], i)
                        a_cen_pos[1] += np.dot(directions[1], i)
                        a_cen_pos[2] += np.dot(directions[2], i)

                        m_cen_pos = max(np.dot(-directions[2], i), m_cen_pos)
                    a_cen_pos[0] /= len(a.positions)      
                    a_cen_pos[1] /= len(a.positions)      
                    a_cen_pos[2] /= len(a.positions)
                    a_cen_pos[2] -= m_cen_pos
          
                  # now find the position
                    cen_pos = np.array([0.0, 0.0, 0.0])
                    if sum(self.images.selected) > 0:
                        for i in range(len(self.R)):
                            if self.images.selected[i]:
                                cen_pos += self.R[i]
                        cen_pos /= sum(self.images.selected)   
                    elif len(self.R) > 0:
                        px = 0.0
                        py = 0.0
                        pz = -1e6

                        for i in range(len(self.R)):
                            px += np.dot(directions[0], self.R[i])
                            py += np.dot(directions[1], self.R[i])
                            pz = max(np.dot(directions[2], self.R[i]), pz)
                        px = (px/float(len(self.R)))
                        py = (py/float(len(self.R)))
                        cen_pos = directions[0] * px + \
                                  directions[1] * py + \
                                  directions[2] * pz
              
                    if 'auto' in pos:
                        pos = pos.replace('auto', '')
                        import re
                        pos = re.sub('\s', '', pos)
                        if '(' in pos:
                            sign = eval('%s1' % pos[0])
                            a_cen_pos -= sign * np.array(eval(pos[1:]), float)
                        else:
                            a_cen_pos -= float(pos) * directions[2]
                    else:
                        cen_pos = np.array(eval(pos))
                    for i in a:
                        i.position += cen_pos - a_cen_pos      
  
                  # and them to the molecule
                    atoms = self.images.get_atoms(self.frame)
                    atoms = atoms + a
                    self.new_atoms(atoms, init_magmom=True)
                    
                  # and finally select the new molecule for easy moving and rotation
                    for i in range(len(a)):
                        self.images.selected[len(atoms) - i - 1] = True

                    self.draw()    
            self.add_entries[0].destroy()
        if data == None:
            molecule = ''
            tag = '0'
            mom = '0'
            pos = 'auto+1'
            self.add_entries = []
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.add_entries.append(window)
            window.set_title('Add atoms')

            vbox = gtk.VBox(False, 0)
            window.add(vbox)
            vbox.show()
            pack = False
            for i, j in [['Insert atom or molecule', molecule],
                         ['Tag', tag],
                         ['Moment', mom],
                         ['Position', pos]]:

                label = gtk.Label(i)
                if not pack:
                    vbox.pack_start(label, True, True, 0)
                else: 
                    pack = True
                    vbox.add(label)    
                label.show()
  
                entry = gtk.Entry()
                entry.set_text(j)
                self.add_entries.append(entry)
                entry.set_max_length(50)
                entry.show()
    
                vbox.add(entry)

            button = gtk.Button('_Load molecule')
            button.connect('clicked', self.add_atoms, 'load')
            button.show()
            vbox.add(button)
            button = gtk.Button('_OK')
            button.connect('clicked', self.add_atoms, 'OK')
            button.show()
            vbox.add(button)
            button = gtk.Button('_Cancel')
            button.connect('clicked', self.add_atoms, 'Cancel')
            button.show()
            vbox.add(button)
 
            window.show()
        
    def modify_atoms(self, widget, data=None):
        """
        Presents a dialog box where the user is able to change the atomic type, the magnetic
        moment and tags of the selected atoms. An item marked with X will not be changed.
        """
        if data:
            if data == 'OK':
                import ase
                symbol = self.add_entries[1].get_text()
                tag = self.add_entries[2].get_text()
                mom = self.add_entries[3].get_text()
                a = None
                if symbol != 'X': 
                    try:
                        a = ase.Atoms([ase.Atom(symbol)])  
                    except:
                        self.add_entries[1].set_text('?' + symbol)
                        return ()
          
                y = self.images.selected.copy()
                    # and them to the molecule
                atoms = self.images.get_atoms(self.frame)
                for i in range(len(atoms)):
                    if self.images.selected[i]:  
                        if a: 
                            atoms[i].symbol = symbol
                        try: 
                            if tag != 'X': 
                                atoms[i].tag = int(tag)
                        except:
                            self.add_entries[2].set_text('?' + tag)
                            return ()
                        try: 
                            if mom != 'X': 
                                atoms[i].magmom = float(mom)
                        except: 
                            self.add_entries[3].set_text('?' + mom)
                            return ()
                self.new_atoms(atoms, init_magmom=True)

                # and finally select the new molecule for easy moving and rotation
                self.images.selected = y
                self.draw()    
          
            self.add_entries[0].destroy()          
        if data == None and sum(self.images.selected):
            atoms = self.images.get_atoms(self.frame)
            s_tag = ''
            s_mom = ''  
            s_symbol = ''
          # Get the tags, moments and symbols of the selected atomsa  
            for i in range(len(atoms)):
                if self.images.selected[i]:
                    if not(s_tag): 
                        s_tag = str(atoms[i].tag)
                    elif s_tag != str(atoms[i].tag): 
                        s_tag = 'X'
                    if not(s_mom): 
                        s_mom = ("%2.2f" % (atoms[i].magmom))
                    elif s_mom != ("%2.2f" % (atoms[i].magmom)): 
                        s_mom = 'X'
                    if not(s_symbol): 
                        s_symbol = str(atoms[i].symbol)       
                    elif s_symbol != str(atoms[i].symbol): 
                        s_symbol = 'X'
  
            self.add_entries = []
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.add_entries.append(window)
            window.set_title('Modify')

            vbox = gtk.VBox(False, 0)
            window.add(vbox)
            vbox.show()
            pack = False
            for i, j in [['Atom', s_symbol],
                        ['Tag', s_tag],
                        ['Moment', s_mom]]:
                label = gtk.Label(i)
                if not pack:
                    vbox.pack_start(label, True, True, 0)
                else: 
                    pack = True
                    vbox.add(label)    
                label.show()

                entry = gtk.Entry()
                entry.set_text(j)
                self.add_entries.append(entry)
                entry.set_max_length(50)
                entry.show()
                vbox.add(entry)
            button = gtk.Button('_OK')
            button.connect('clicked', self.modify_atoms, 'OK')
            button.show()
            vbox.add(button)
            button = gtk.Button('_Cancel')
            button.connect('clicked', self.modify_atoms, 'Cancel')
            button.show()
            vbox.add(button)
 
            window.show()
        
    def delete_selected_atoms(self, widget=None, data=None):
        if data == 'OK':
            atoms = self.images.get_atoms(self.frame)
            lena = len(atoms)
            for i in range(len(atoms)):
                li = lena-1-i
                if self.images.selected[li]:
                    del(atoms[li])
            self.new_atoms(atoms)
         
            self.draw()    
        if data:      
            self.delete_window.destroy()
             
        if not(data) and sum(self.images.selected):
            more = '' + (sum(self.images.selected) > 1) * 's'
            self.delete_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.delete_window.set_title('Confirmation')
            self.delete_window.set_border_width(10)
            self.box1 = gtk.HBox(False, 0)
            self.delete_window.add(self.box1)
            self.button1 = gtk.Button('Delete selected atom%s?' % more)
            self.button1.connect("clicked", self.delete_selected_atoms, "OK")
            self.box1.pack_start(self.button1, True, True, 0)
            self.button1.show()

            self.button2 = gtk.Button("Cancel")
            self.button2.connect("clicked", self.delete_selected_atoms, "Cancel")
            self.box1.pack_start(self.button2, True, True, 0)
            self.button2.show()

            self.box1.show()
            self.delete_window.show()
                
    def debug(self, x):
        from ase.gui.debug import Debug
        Debug(self)

    def execute(self, widget=None):
        from ase.gui.execute import Execute
        Execute(self)
        
    def constraints_window(self, widget=None):
        from ase.gui.constraints import Constraints
        Constraints(self)

    def dft_window(self, widget=None):
        from ase.gui.dft import DFT
        DFT(self)

    def select_all(self, widget):
        self.images.selected[:] = True
        self.draw()
        
    def invert_selection(self, widget):
        self.images.selected[:] = ~self.images.selected
        self.draw()
        
    def select_constrained_atoms(self, widget):
        self.images.selected[:] = ~self.images.dynamic
        self.draw()
        
    def movie(self, widget=None):
        from ase.gui.movie import Movie
        self.movie_window = Movie(self)
        
    def plot_graphs(self, x=None, expr=None):
        from ase.gui.graphs import Graphs
        g = Graphs(self)
        if expr is not None:
            g.plot(expr=expr)
        self.graph_wref.append(weakref.ref(g))

    def plot_graphs_newatoms(self):
        "Notify any Graph objects that they should make new plots."
        new_wref = []
        found = 0
        for wref in self.graph_wref:
            ref = wref()
            if ref is not None:
                ref.plot()
                new_wref.append(wref)  # Preserve weakrefs that still work.
                found += 1
        self.graph_wref = new_wref
        return found
        
    def NEB(self, action):
        from ase.gui.neb import NudgedElasticBand
        NudgedElasticBand(self.images)
        
    def bulk_modulus(self, action):
        from ase.gui.bulk_modulus import BulkModulus
        BulkModulus(self.images)
        
    def open(self, button=None, filenames=None):
        if filenames == None:
            chooser = gtk.FileChooserDialog(
                _('Open ...'), None, gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            ok = chooser.run() == gtk.RESPONSE_OK
            if ok:
                filenames = [chooser.get_filename()]
            chooser.destroy()

            if not ok:
                return

        n_current = self.images.nimages
        self.reset_tools_modes()     
        self.images.read(filenames, slice(None))
        self.set_colors()
        self.set_coordinates(self.images.nimages - 1, focus=True)

    def import_atoms (self, button=None, filenames=None):
        if filenames == None:
            chooser = gtk.FileChooserDialog(
                _('Open ...'), None, gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            ok = chooser.run()
            if ok == gtk.RESPONSE_OK:
                filenames = [chooser.get_filename()]
            chooser.destroy()

            if not ok:
                return
            
            
        self.images.import_atoms(filenames, self.frame)
        self.set_colors()
        self.set_coordinates(self.images.nimages - 1, focus=True)

    def save(self, action):
        chooser = gtk.FileChooserDialog(
            _('Save ...'), None, gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        # Add a file type filter
        types = []
        name_to_suffix = {}
        for name, suffix in [('Automatic', None),
                             ('XYZ file', 'xyz'),
                             ('ASE trajectory', 'traj'),
                             ('PDB file', 'pdb'),
                             ('Gaussian cube file', 'cube'),
                             ('Python script', 'py'),
                             ('VNL file', 'vnl'),
                             ('Portable Network Graphics', 'png'),
                             ('Persistance of Vision', 'pov'),
                             ('Encapsulated PostScript', 'eps'),
                             ('FHI-aims geometry input', 'in'),
                             ('VASP geometry input', 'POSCAR'),
                             ('ASE bundle trajectory', 'bundle'),
                             ]:
            if suffix is None:
                name = _(name)
            else:
                name = '%s (%s)' % (_(name), suffix)
            filt = gtk.FileFilter()
            filt.set_name(name)
            if suffix is None:
                filt.add_pattern('*')
            elif suffix == 'POSCAR':
                filt.add_pattern('*POSCAR*')
            else:
                filt.add_pattern('*.'+suffix)
            if suffix is not None:
                types.append(suffix)
                name_to_suffix[name] = suffix
                
            chooser.add_filter(filt)

        if self.images.nimages > 1:
            img_vbox = gtk.VBox()
            button = gtk.CheckButton('Save current image only (#%d)' %
                                     self.frame)
            pack(img_vbox, button)
            entry = gtk.Entry(10)
            pack(img_vbox, [gtk.Label(_('Slice: ')), entry,
                                        help('Help for slice ...')])
            entry.set_text('0:%d' % self.images.nimages)
            img_vbox.show()
            chooser.set_extra_widget(img_vbox)

        while True:
            # Loop until the user selects a proper file name, or cancels.
            response = chooser.run()
            if response == gtk.RESPONSE_CANCEL or response == gtk.RESPONSE_DELETE_EVENT:
                chooser.destroy()
                return
            elif response != gtk.RESPONSE_OK:
                print >>sys.stderr, "AG INTERNAL ERROR: strange response in Save,", response
                chooser.destroy()
                return
                
            filename = chooser.get_filename()

            suffix = os.path.splitext(filename)[1][1:]
            if 'POSCAR' in filename:
                suffix = 'POSCAR'
            if suffix == '':
                # No suffix given.  If the user has chosen a special
                # file type, use the corresponding suffix.
                filt = chooser.get_filter().get_name()
                suffix = name_to_suffix[filt]
                filename = filename + '.' + suffix
                
            if suffix not in types:
                oops(message='Unknown output format!',
                     message2='Use one of: ' + ', '.join(types[1:]))
                continue
                
            if self.images.nimages > 1:
                if button.get_active():
                    filename += '@%d' % self.frame
                else:
                    filename += '@' + entry.get_text()

            break
        
        chooser.destroy()

        bbox = np.empty(4)
        size = np.array([self.width, self.height]) / self.scale
        bbox[0:2] = np.dot(self.center, self.axes[:, :2]) - size / 2
        bbox[2:] = bbox[:2] + size
        suc = self.ui.get_widget('/MenuBar/ViewMenu/ShowUnitCell').get_active()
        self.images.write(filename, self.axes, show_unit_cell=suc, bbox=bbox)
        
    def quick_info_window(self, menuitem):
        QuickInfo(self)

    def bulk_window(self, menuitem):
        SetupBulkCrystal(self)

    def surface_window(self, menuitem):
        SetupSurfaceSlab(self)

    def nanoparticle_window(self, menuitem):
        SetupNanoparticle(self)
        
    def graphene_window(self, menuitem):
        SetupGraphene(self)

    def nanotube_window(self, menuitem):
        SetupNanotube(self)

    def calculator_window(self, menuitem):
        SetCalculator(self)
        
    def energy_window(self, menuitem):
        EnergyForces(self)
        
    def energy_minimize_window(self, menuitem):
        Minimize(self)

    def scaling_window(self, menuitem):
        HomogeneousDeformation(self)
        
    def new_atoms(self, atoms, init_magmom=False):
        "Set a new atoms object."
        self.reset_tools_modes()
        
        rpt = getattr(self.images, 'repeat', None)
        self.images.repeat_images(np.ones(3, int))
        self.images.initialize([atoms], init_magmom=init_magmom)
        self.frame = 0   # Prevent crashes
        self.images.repeat_images(rpt)
        self.set_colors()
        self.set_coordinates(frame=0, focus=True)
        self.notify_vulnerable()

    def prepare_new_atoms(self):
        "Marks that the next call to append_atoms should clear the images."
        self.images.prepare_new_atoms()
        
    def append_atoms(self, atoms):
        "Set a new atoms object."
        #self.notify_vulnerable()   # Do this manually after last frame.
        frame = self.images.append_atoms(atoms)
        self.set_coordinates(frame=frame-1, focus=True)

    def notify_vulnerable(self):
        """Notify windows that would break when new_atoms is called.

        The notified windows may adapt to the new atoms.  If that is not
        possible, they should delete themselves.
        """
        new_vul = []  # Keep weakrefs to objects that still exist.
        for wref in self.vulnerable_windows:
            ref = wref()
            if ref is not None:
                new_vul.append(wref)
                ref.notify_atoms_changed()
        self.vulnerable_windows = new_vul

    def register_vulnerable(self, obj):
        """Register windows that are vulnerable to changing the images.

        Some windows will break if the atoms (and in particular the
        number of images) are changed.  They can register themselves
        and be closed when that happens.
        """
        self.vulnerable_windows.append(weakref.ref(obj))

    def exit(self, button, event=None):
        self.window.destroy()
        gtk.main_quit()
        return True

    def xxx(self, x=None,
            message1='Not implemented!',
            message2='do you really need it?'):
        oops(message1, message2)
        
    def about(self, action):
        try:
            dialog = gtk.AboutDialog()
        except AttributeError:
            self.xxx()
        else:
            dialog.run()

def webpage(widget):
    import webbrowser
    webbrowser.open('https://wiki.fysik.dtu.dk/ase/ase/gui.html')

