
from config import AstroConfig
from observatory import Observatory
from nea import NASAExoplanetArchive
from exoticjsoninit import ExoticJsonInit
from fitsfile import FitsFile
from aavso import AAVSO

import json

def main():
    try:

        # load config file
        config = AstroConfig()

        # get minimal input for observatory and planet

        # observatory data for json and aavso url
        obs_number = input(f"Select Observatory:\n1. Whipple\n2. CAS (not ready)\n(1-default):")
        observatory = Observatory(int(obs_number), config)
        if observatory.observatoryJson is None:
            observatory = Observatory(1, config)

        # planet data for json
        planet = input(f"Planet name (ex: TRES-3 b): ")
        #################!!!!!!!!!!!!!!!!!!!!!
        # remove this
        # planet = "WASP-43 b"
        # get planet data
        initplanet = NASAExoplanetArchive(planet=planet)
        pDict = initplanet.planet_info()
        planetObj = initplanet.planet_info(fancy=True)

        # this relies on the planet being entered correctly
        star_name = planet.split(" ")[0]

        # replace observatory data with config params
        if observatory.obs_data is not None:

            jsonInit = ExoticJsonInit(observatory.obs_data, config)
            jsonInit.setUserInfoJsonData(planet)
            jsonInit.setPlanetJsonData(planetObj)

            fitsFileObject = FitsFile(config)
            fitsFile = fitsFileObject.find_first_gz_file(config.fits_files_dir + planet.replace(" ", "") + "/")

            if fitsFile:

                date_obs = fitsFileObject.get_observation_date()
                observatory.setObservationDate(date_obs)

                aavsoData = AAVSO(config, star_name, observatory, fitsFileObject)
                targetarray, comparray = aavsoData.getTargetCompArray()

                if targetarray is not None and comparray is not None:
                    observatory.setTargetCompData(targetarray, comparray)

                # print(json.dumps(jsonInit.obs_data))
                # save planet data to disk
                json_file = config.fits_files_dir + planet.replace(" ", "") + "_" + date_obs + "_inits.json"
                # print(obs_data)
                print("Use this file path when EXOTIC asks for a json file:\n" + json_file)
                with open(json_file, 'w') as f:
                    f.write(json.dumps(jsonInit.obs_data))

                chartImgPath = AAVSO.getAAVSOChartImagePath()
                fitsImage = AAVSO.getFITSImage()

            else:
                print("No .gz file found in the directory")
        else:
            print("Error getting observatory information")

    except Exception as e:
        print("Error in exotic-prep: " + str(e))

if __name__ == "__main__":
    main()
