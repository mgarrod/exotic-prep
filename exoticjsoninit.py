import json

class ExoticJsonInit:
    def __init__(self, obs_data, config):

        self.obs_data = obs_data
        self.config = config

    def setUserInfoJsonData(self, planet):
        self.obs_data["user_info"]["Directory with FITS files"] = self.config.fits_files_dir + planet.replace(" ", "") + "/"
        self.obs_data["user_info"]["Directory to Save Plots"] = self.config.output_dir
        self.obs_data["user_info"]["AAVSO Observer Code (N/A if none)"] = self.config.obs_code

        if self.config.flats is not None:
            self.observatory.obs_data["user_info"]["Directory of Flats"] = self.config.fits_files_dir + planet.replace(" ",
                                                                                                             "") + "/" + self.config.flats + "/"
        if self.config.darks is not None:
            self.obs_data["user_info"]["Directory of Darks"] = self.config.fits_files_dir + planet.replace(" ",
                                                                                                             "") + "/" + self.config.darks + "/"
        if self.config.biases is not None:
            self.obs_data["user_info"]["Directory of Biases"] = self.config.fits_files_dir + planet.replace(" ",
                                                                                                              "") + "/" + self.config.biases + "/"
    def setPlanetJsonData(self, planetObj):
        # add planet data to init json
        self.obs_data["planetary_parameters"] = json.loads(planetObj)
