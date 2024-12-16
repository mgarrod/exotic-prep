
from config import AstroConfig
from observatory import Observatory
from nea import NASAExoplanetArchive
from exoticjsoninit import ExoticJsonInit
from fitsfile import FitsFile
from aavso import AAVSO

import json
from PIL import Image

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

        filter = input(f"Filter (V-default):")
        if filter == "":
            filter = "V"
        

        # planet data for json
        planet = input(f"Planet name (ex: TRES-3 b): ")
        #################!!!!!!!!!!!!!!!!!!!!!
        # remove this
        # planet = "WASP-43 b"
        # get planet data
        initplanet = NASAExoplanetArchive(planet=planet)
        pDict = initplanet.planet_info()
        planetObj = initplanet.planet_info(fancy=True)
        
        planet = pDict['pName']
        star_name = pDict['sName']

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

                chartImgPath = aavsoData.getAAVSOChartImagePath()
                fitsImage = aavsoData.getFITSImage()

                # Open the two images
                fitsImage = Image.open(fitsImage)
                chartImgPath = Image.open(chartImgPath)

                # Get the dimensions of the images
                width1, height1 = fitsImage.size
                width2, height2 = chartImgPath.size

                # Determine which image is smaller and resize it
                if height1 < height2:
                    new_width1 = int(width1 * (height2 / height1))
                    fitsImage = fitsImage.resize((new_width1, height2))
                else:
                    new_width2 = int(width2 * (height1 / height2))
                    chartImgPath = chartImgPath.resize((new_width2, height1))

                # Create a new image with a width that is the sum of both images' widths and the height of the taller image
                new_image = Image.new('RGB', (fitsImage.width + chartImgPath.width, max(height1, height2)))

                # Paste the images into the new image
                new_image.paste(fitsImage, (0, 0))
                new_image.paste(chartImgPath, (fitsImage.width, 0))

                # Save the new image
                output_jpg = config.output_dir + star_name + "_combined_image.jpg"
                new_image.save(output_jpg)
                print(f"Combined image saved as {output_jpg}")

            else:
                print("No .gz file found in the directory")
        else:
            print("Error getting observatory information")

    except Exception as e:
        print("Error in exotic-prep: " + str(e))

if __name__ == "__main__":
    main()
