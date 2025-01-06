import json
import os

class ExoticJsonInit:
    def __init__(self, obs_data, config):

        self.obs_data = obs_data
        self.config = config

    def setUserInfoJsonData(self, planet):
        self.obs_data["user_info"]["Directory with FITS files"] = self.config.fits_files_dir
        self.obs_data["user_info"]["Directory to Save Plots"] = self.config.output_dir
        self.obs_data["user_info"]["AAVSO Observer Code (N/A if none)"] = self.config.aavso_observer_code

        if self.config.flats:
            self.obs_data["user_info"]["Directory of Flats"] = os.path.join(self.config.fits_files_dir, "flats")
        if self.config.darks:
            self.obs_data["user_info"]["Directory of Darks"] = os.path.join(self.config.fits_files_dir, "darks")
        if self.config.biases:
            self.obs_data["user_info"]["Directory of Biases"] = os.path.join(self.config.fits_files_dir, "biases")
    def setPlanetJsonData(self, planetObj):
        # add planet data to init json
        self.obs_data["planetary_parameters"] = json.loads(planetObj)
