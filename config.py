import configparser
import os

class AstroConfig:
    def __init__(self):

        self._pyfile_dir = os.path.dirname(os.path.abspath(__file__))

        config = self.load_config(self.pyfile_dir + "/config.ini")
        self.fits_files_dir = config.get("REQUIRED", "fits_files_dir")
        self.output_dir = config.get("REQUIRED", "output_dir")
        self.aavso_observer_code = config.get("REQUIRED", "aavso_observer_code")
        self.ast_api_key = config.get("REQUIRED", "ast_api_key")
        self.flats = config.get("OPTIONAL", "flats")
        self.darks = config.get("OPTIONAL", "darks")
        self.biases = config.get("OPTIONAL", "biases")
        if (self.flats == "None"):
            self.flats = None
        if (self.darks == "None"):
            self.darks = None
        if (self.biases == "None"):
            self.biases = None

    def load_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    @property
    def pyfile_dir(self):
        return self._pyfile_dir

    @pyfile_dir.setter
    def pyfile_dir(self, value):
        self._pyfile_dir = value

    @property
    def fits_files_dir(self):
        return self._fits_files_dir

    @fits_files_dir.setter
    def fits_files_dir(self, value):
        self._fits_files_dir = value

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value

    @property
    def aavso_observer_code(self):
        return self._aavso_observer_code

    @aavso_observer_code.setter
    def obs_code(self, value):
        self._aavso_observer_code = value

    @property
    def ast_api_key(self):
        return self._ast_api_key

    @ast_api_key.setter
    def ast_api_key(self, value):
        self._ast_api_key = value

    @property
    def flats(self):
        return self._flats

    @flats.setter
    def flats(self, value):
        self._flats = value

    @property
    def darks(self):
        return self._darks

    @darks.setter
    def darks(self, value):
        self._darks = value

    @property
    def biases(self):
        return self._biases

    @biases.setter
    def biases(self, value):
        self._biases = value
