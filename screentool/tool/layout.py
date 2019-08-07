import binascii
import logging
import os

from Xlib import X, display
from Xlib.ext import randr


class LayoutManager:
    logger = logging.getLogger('LayoutManager')

    def __init__(self, configManager):
        self.configManager = configManager

        self.display = display.Display()
        self.screen = self.display.screen() # Screen as an X11 screen, not the actual output
        self.window = self.screen.root.create_window(0, 0, 1, 1, 1, self.screen.root_depth)
        outputs = randr.get_screen_resources(self.window).outputs

        self.logger.debug('Found [{}] outputs available'.format(len(outputs)))

        self.outputs = []
        for output in outputs:
            outInfo = randr.get_output_info(self.window, output, 0)

            if outInfo.connection == 0:
                self.logger.debug('Output [{}] is connected'.format(outInfo.name))

            if outInfo.crtc > 0:
                self.logger.debug('Output [{}] is rendered'.format(outInfo.name))
                edid = self.__getEDID(output)
                if edid is None:
                    self.logger.info('Output [{}] cannot be identified, skipping ...'.format(outInfo.name))
                else:
                    # Resolve the CRTC of the output
                    self.outputs.append({
                        'edid': edid,
                        'crtc': self.__getCRTC(outInfo),
                        'info': outInfo
                    })

    def apply(self, layoutId):
        pass

    def list(self):
        for layout in self.configManager.layout():
            print(layout['id'])

    def register(self):
        outputConfig = []
        for output in self.outputs:
            outputConfig.append({
                'edid': output['edid'],
                'name': output['info'].name, # Only  used for display
                'height': output['crtc'].height, # Only  used for display
                'width': output['crtc'].width, # Only  used for display
                'crtc': output['info'].crtc,
                'x': output['crtc'].x,
                'y': output['crtc'].y
            })

        payload = {
            'outputs': outputConfig,
            'id': binascii.b2a_hex(os.urandom(8)).decode('UTF-8')
        }

        self.configManager.layouts().append(payload)
        self.configManager.persist()

    def status(self):
        for output in self.outputs:
            print('Output [{}] : {}x{} at position ({}, {})'
                  .format(output['info'].name,
                          output['crtc'].width,
                          output['crtc'].height,
                          output['crtc'].x,
                          output['crtc'].y))

    # Get the list of available screen properties
    # Then search for the "EDID" atom code
    def __getEDID(self, output):
        availableProps = randr.list_output_properties(self.window, output)
        for atom in availableProps.atoms:
            atomName = self.display.get_atom_name(atom)
            if atomName == randr.PROPERTY_RANDR_EDID:
                out = randr.get_output_property(self.window, output, atom, X.AnyPropertyType, 0, 100, False, False)
                edid = binascii.hexlify(bytearray(out.value)).decode('UTF-8')
                self.logger.debug('Output EDID : [{}]'.format(edid))
                return edid
        return None

    # Fetch the information about the current CRTC used by the output
    def __getCRTC(self, outInfo):
        return randr.get_crtc_info(self.window, outInfo.crtc, outInfo.timestamp)
