import binascii
import logging

from Xlib import X, display
from Xlib.ext import randr


class LayoutManager:
    logger = logging.getLogger('LayoutManager')

    def __init__(self, configManager):
        self.configManager = configManager

        disp = display.Display()
        screen = disp.screen() # Screen as an X11 screen, not the actual output
        window = screen.root.create_window(0, 0, 1, 1, 1, screen.root_depth)
        outputs = randr.get_screen_resources(window).outputs

        self.logger.debug('Found [{}] outputs available'.format(len(outputs)))

        self.outputs = []
        for output in outputs:
            outInfo = randr.get_output_info(window, output, 0)

            if outInfo.connection == 0:
                self.logger.debug('Output [{}] is connected'.format(outInfo.name))

            if outInfo.crtc > 0:
                self.logger.debug('Output [{}] is rendered'.format(outInfo.name))
                edid = self.__getEDID(disp, window, output)
                if edid is None:
                    self.logger.info('Output [{}] cannot be identified, skipping ...'.format(outInfo.name))
                else:
                    self.outputs.append({
                        'edid': edid,
                        'output': output
                    })

    def register(self):
        pass

    def list(self):
        for layout in self.configManager.layout():
            print(layout['id'])

    def apply(self, layoutId):
        pass

    # Get the list of available screen properties
    # Then search for the "EDID" atom code
    def __getEDID(self, disp, window, output):
        availableProps = randr.list_output_properties(window, output)
        for atom in availableProps.atoms:
            atomName = disp.get_atom_name(atom)
            if atomName == randr.PROPERTY_RANDR_EDID:
                out = randr.get_output_property(
                    window, output, atom,
                    X.AnyPropertyType, 0, 100, False, False)
                edid = binascii.hexlify(bytearray(out.value))
                self.logger.debug('Output EDID : [{}]'.format(edid))
                return edid
        return None
