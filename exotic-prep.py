
from config import AstroConfig
from observatory import Observatory
from nea import NASAExoplanetArchive
from exoticjsoninit import ExoticJsonInit
from fitsfile import FitsFile
from aavso import AAVSO

import json
from PIL import Image

import os
# remove
# os.environ["REQUESTS_CA_BUNDLE"] = "/Users/mgarrod/Development/certs/ca4.cer"

def main():
    try:

        # load config file
        config = AstroConfig()

        # get minimal input for observatory and planet

        # observatory data for json and aavso url
        obs_number = input(f"\nObservatories:\n          1. Whipple (default)\n\nChoose an observatory:")
        try:
            obs_number = int(obs_number)
        except:
            obs_number = 1
        observatory = Observatory(obs_number, config)
        if observatory.observatoryJson is None:
            observatory = Observatory(1, config)

        filter = input(f"\nFilter (default: MObs CV):")
        if filter == "":
            filter = "MObs CV"

        # planet data for json
        planet = input(f"\nPlanet name (ex: TRES-3 b): ")
        #################!!!!!!!!!!!!!!!!!!!!!
        # remove this
        #planet = "WASP-43 b"

        # get dir where files are
        fitsDir = input(f"\nFolder Name where the FITS files for " + planet + " are located.\n(The folder should be located in this directory: " + config.fits_files_dir + "):")
        #################!!!!!!!!!!!!!!!!!!!!!
        # remove this
        #fitsDir = "WASP-43 b"

        # calibration
        print("\nIf there are calibration FITS files, they need to be inside folders named: flats, darks, and biases. These folders should be inside the \"" + fitsDir + "\" directory.")
        flats = input(f"Are there flat calibration images (default: no)? (y/n):")
        if flats.lower() == "y" or flats.lower() == "yes":
            config.flats = True
        darks = input(f"Are there dark calibration images (default: no)? (y/n):")
        if darks.lower() == "y" or darks.lower() == "yes":
            config.darks = True
        biases = input(f"Are there bias calibration images (default: no)? (y/n):")
        if biases.lower() == "y" or biases.lower() == "yes":
            config.biases = True

        config.fits_files_dir = os.path.join(config.fits_files_dir, fitsDir)

        # set output
        config.output_dir = os.path.join(config.fits_files_dir, "output")
        if not os.path.isdir(config.output_dir):
            try:
                os.makedirs(config.output_dir)
            except:
                print("Error creating output directory in " + config.fits_files_dir + ". Please verify your settings in config.ini are correct.")

        # get planet data
        initplanet = NASAExoplanetArchive(planet=planet)
        pDict = initplanet.planet_info()
        planetObj = initplanet.planet_info(fancy=True)

        # set the planet and star name to proper
        planetJson = json.loads(planetObj)
        planet = planetJson["Planet Name"]
        star_name = planetJson["Host Star Name"]

        # replace observatory data with config params
        if observatory.obs_data is not None:

            # set the filter in the json
            observatory.setObservationFilter(filter)

            jsonInit = ExoticJsonInit(observatory.obs_data, config)
            jsonInit.setUserInfoJsonData(planet)
            jsonInit.setPlanetJsonData(planetObj)

            fitsFileObject = FitsFile(config)
            fitsFile = fitsFileObject.find_first_gz_file(config.fits_files_dir)
            print(fitsFile)

            if fitsFile:

                date_obs = fitsFileObject.get_observation_date()
                observatory.setObservationDate(date_obs)

                aavsoData = AAVSO(config, star_name, observatory, fitsFileObject)
                targetarray, comparray, compmagarray = aavsoData.getTargetCompArray()

                if targetarray is not None and comparray is not None:
                    observatory.setTargetCompData(targetarray, comparray)

                # print(json.dumps(jsonInit.obs_data))
                # save planet data to disk
                json_file = os.path.join(config.output_dir, planet.replace(" ", "") + "_" + date_obs + "_inits.json")
                # print(obs_data)
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
                output_jpg = os.path.join(config.output_dir, star_name + "_combined_image.jpg")
                new_image.save(output_jpg)
                print("###########################################################\n\nCombined image saved as \"" + output_jpg + "\"\n")

                exotic_cmd = "exotic -red \"" + json_file + "\" -ov"
                print("Use this command to run exotic:\n" + exotic_cmd + "\n")
                print("###########################################################")

            else:
                print("No .gz file found in the directory")
        else:
            print("Error getting observatory information")

    except Exception as e:
        print("Error in exotic-prep: " + str(e))

if __name__ == "__main__":
    main()
