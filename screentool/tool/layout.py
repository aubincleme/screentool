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

        # Detect the outputs
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
                    crtc = self.__getCRTC(outInfo)
                    self.outputs.append({
                        'output': output,
                        'info': outInfo,
                        'crtc': crtc,
                        'meta': {
                            'edid': edid,
                            'name': outInfo.name,
                            'height': crtc.height,
                            'width': crtc.width,
                            'crtc': outInfo.crtc,
                            'x': crtc.x,
                            'y': crtc.y,
                            'mode': crtc.mode,
                            'rotation': crtc.rotation
                        }
                    })

    def configure(self):
        # Look for a matching configuration in the registered layouts
        # The edids of the connected screens
        edids = [output['meta']['edid'] for output in self.outputs]
        edids.sort()
        for layout in self.configManager.layouts():
            layoutEDID = [output['edid'] for output in layout['outputs']]
            layoutEDID.sort()
            if edids == layoutEDID:
                self.logger.debug('Found matching configuration : [{}]'.format(layout['id']))

                # Go through each output and configure their CRTC.
                for output in self.outputs:
                    # Get the corresponding output in the registered layout
                    referenceOutput = [refOut for refOut in layout['outputs']
                                       if refOut['edid'] == output['meta']['edid']][0]
                    result = randr.set_crtc_config(self.window,
                                                   output['info'].crtc,
                                                   output['info'].timestamp,
                                                   int(referenceOutput['x']),
                                                   int(referenceOutput['y']),
                                                   int(referenceOutput['mode']),
                                                   int(referenceOutput['rotation']),
                                                   [output['output']])
                return

        # At this point, we've not been able to find a correct configuration
        self.logger.info('No matching configuration found. Exiting.')
        return

    def list(self):
        for layout in self.configManager.layouts():
            print('Layout {} :'.format(layout['id']))
            for output in layout['outputs']:
                print('|-> Output [{}] ({}x{}) at ({},{})'
                      .format(output['name'],
                              output['width'],
                              output['height'],
                              output['x'],
                              output['y']))

    def register(self):
        payload = {
            'outputs': [output['meta'] for output in self.outputs],
            'id': binascii.b2a_hex(os.urandom(4)).decode('UTF-8')
        }

        self.configManager.layouts().append(payload)
        self.configManager.persist()

    def status(self):
        for output in self.outputs:
            meta = output['meta']
            print('Output [{}] : {}x{} at ({}, {})'
                  .format(meta['name'],
                          meta['width'],
                          meta['height'],
                          meta['x'],
                          meta['y']))

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
