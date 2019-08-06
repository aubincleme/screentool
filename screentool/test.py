from Xlib import X, display
from Xlib.ext import randr

from Xlib.ext.randr import PROPERTY_RANDR_EDID

import Xlib

import pdb

d = display.Display()
s = d.screen()
window = s.root.create_window(0, 0, 1, 1, 1, s.root_depth)

res = randr.get_screen_resources(window)


for mode in res.modes:
    w, h = mode.width, mode.height
    print("Width: {}, height: {}".format(w, h))

outputs = randr.get_screen_resources(window).outputs

for output in outputs:
    outInfo = randr.get_output_info(window, output, 0)


    if outInfo.connection == 0:
        print("{} connected".format(outInfo.name))

    if outInfo.crtc > 0:
        print("{} rendered".format(outInfo.name))
        print("OUT PROPERTY")
        availableProps = randr.list_output_properties(window, output)
        for atom in availableProps.atoms:
            atomName = d.get_atom_name(atom)

            if atomName == randr.PROPERTY_RANDR_EDID:
                print("{} - {}".format(atom, atomName))
                out = randr.get_output_property(window, output, atom, X.AnyPropertyType, 0, 100, False, False)
                print(out)

        #print(outInfo)
