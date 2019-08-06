import json
import logging
import os
import os.path


class Environment:
    toolDir = '{}/.screentool'.format(os.getenv("HOME"))
    configFilePath = '{}/config.json'.format(toolDir)


class ConfigManager:
    logger = logging.getLogger('ConfigManager')

    defaultConfig = {
        'presets': []
    }

    def __init__(self):
        self.__ensureExistingFolders()
        self.__loadConfig()

    def __ensureExistingFolders(self):
        foldersToCheck = [Environment.toolDir]

        for folder in foldersToCheck:
            self.logger.debug('Checking directory {}'.format(folder))
            if not os.path.isdir(folder):
                self.logger.info('Creating directory {}'.format(folder))
                os.makedirs(folder)

    # Load the configuration content
    def __loadConfig(self):
        baseConfigDir = os.path.dirname(Environment.configFilePath)

        if not os.path.exists(baseConfigDir):
            self.logger.info('No configuration directory found, creating {}.'.format(baseConfigDir))
            os.makedirs(baseConfigDir)

        if not os.path.isfile(Environment.configFilePath):
            self.logger.info(
                    'No configuration file found, creating a new one in {}.'.format(Environment.configFilePath))
            self.config = self.defaultConfig
            self.__saveConfig()
        else:
            with open(Environment.configFilePath, 'r+') as configFile:
                self.config = json.load(configFile)
                self.logger.debug(self.config)

    def __saveConfig(self):
        dumps = json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))
        with open(Environment.configFilePath, 'w+') as configFile:
            configFile.write(dumps)

    def layouts(self):
        return self.config['layouts']

    def persist(self):
        self.__saveConfig()
