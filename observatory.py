import json
import os

class Observatory:
    def __init__(self, obs_number, config):
        self.obs_number = obs_number
        self.data = self.load_data(obs_number)
        self.config = config
        self.obs_data = self.getObservatoryJson()

    def load_data(self, obs_number):
        data = {
            1: {
                "observatoryJson": "whipple.json",
                "fov": 56.44,
                "maglimit": 15,
                "resolution": 150,
                "scale": "D"
            },
            2: {
                "observatoryJson": "fortyeightforest.json",
                "fov": 30,
                "maglimit": 15,
                "resolution": 150,
                "scale": "E"
            },
            3: {
                "observatoryJson": "cas.json",
                "fov": -1,
                "maglimit": -1,
                "resolution": -1,
                "scale": "D"
            }
        }
        return data.get(obs_number, {})

    def getObservatoryJson(self):
        obs_data = None
        with open(os.path.join(self.config.pyfile_dir, "observatories", self.observatoryJson), "r") as rawjson:
            obs_data = json.load(rawjson)
        return obs_data

    def setObservationFilter(self, filter):
        self.obs_data["user_info"]["Filter Name (aavso.org/filters)"] = filter

    def setObservationDate(self, date_obs):
        self.obs_data["user_info"]["Observation date"] = date_obs

    def setTargetCompData(self, targetarray, comparray):
        self.obs_data["user_info"]["Target Star X & Y Pixel"] = targetarray
        self.obs_data["user_info"]["Comparison Star(s) X & Y Pixel"] = comparray

    @property
    def observatoryJson(self):
        return self.data.get("observatoryJson", None)

    @property
    def fov(self):
        return self.data.get("fov", None)

    @property
    def maglimit(self):
        return self.data.get("maglimit", None)

    @property
    def resolution(self):
        return self.data.get("resolution", None)

    @property
    def scale(self):
        return self.data.get("scale", None)

