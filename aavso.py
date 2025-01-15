from astroquery.simbad import Simbad
import astropy.units as u
from astropy.coordinates import Angle
from astropy.wcs import WCS
from astroquery.astrometry_net import AstrometryNet
import requests
import json
import numpy as np
import os
import math

class AAVSO:
    def __init__(self, config, starname, observatory, fitsFileObject):

        self.config = config
        self.starname = starname
        self.observatory = observatory
        self.fitsFileObject = fitsFileObject

        self.targetarray = None
        self.comparray = None
        self.compmagarray = None
        self.ast = AstrometryNet()
        self.ast.api_key = self.config.ast_api_key
        self.aavso_chart_url = None

    def get_star_magnitude(self, starname):

        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('flux(V)')
        result = custom_simbad.query_object(starname)
        if result is None:
            return result
        magnitude = None
        try:
            magnitude = result['FLUX_V'][0]
        except:
            magnitude = None
        return magnitude

    def convert_to_decimal_degrees(self, ra_str, dec_str):
        ra = Angle(ra_str, unit=u.hourangle)
        dec = Angle(dec_str, unit=u.deg)
        return ra.degree, dec.degree

    def getAAVSOChartImagePath(self):

        response = requests.get(self.aavso_chart_url)
        if response.status_code == 200:
            aavso_outfile = os.path.join(self.config.output_dir, "AAVSO_" + self.starname + "_Chart.jpg")
            with open(aavso_outfile, "wb") as file:
                file.write(response.content)
            #print(f"AAVSO image saved as {aavso_outfile}")

            return aavso_outfile
        else:
            print("Failed to retrieve the AAVSO image.")
            return None

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def remove_close_points(self, coords, min_distance):
        indexes_to_remove = []
        original_indexes = list(range(len(coords)))

        while coords:
            x1, y1 = coords.pop(0)
            original_index = original_indexes.pop(0)

            to_remove = []
            for i, (x2, y2) in enumerate(coords):
                if self.distance(x1, y1, x2, y2) < min_distance:
                    to_remove.append(i)

            for i in reversed(to_remove):
                coords.pop(i)
                indexes_to_remove.append(original_indexes.pop(i))

        return indexes_to_remove

    def getFITSImage(self):

        comparraycolor = ["red"] * len(self.comparray)
        comparraycolor.insert(0, "green")

        comparraytmp = self.comparray
        comparraytmp.insert(0, self.targetarray)

        compmagarraytmp = self.compmagarray
        compmagarraytmp.insert(0, -1)

        output_png = os.path.join(self.config.output_dir, self.starname + "_and_comp_coordinates.png")
        self.fitsFileObject.convert_fits_to_png_with_markers(output_png, comparraytmp, comparraycolor, compmagarraytmp, self.starname)
        #print(f"Target and Comp Star image saved as {output_png}")

        return output_png

    def getTargetCompArray(self):

        magnitude = self.get_star_magnitude(self.starname)
        print(f"Star magnitude: {magnitude}")

        aavsourl = "https://apps.aavso.org/vsp/api/chart/?star=" + self.starname + "&scale=" + self.observatory.scale + "&orientation=CCD&type=chart&fov=" + str(
            self.observatory.fov) + "&maglimit=" + str(self.observatory.maglimit) + "&resolution=" + str(
            self.observatory.resolution) + "&north=down&east=left&lines=True&format=json"
        aavsores = requests.get(aavsourl)

        aavso = None
        try:
            aavso = json.loads(aavsores.text)
        except:
            print("Error getting data from AAVSO. Their site may be down. Please try again later.")
            exit(0)

        self.aavso_chart_url = aavso["image_uri"]

        target_ra = aavso["ra"]
        target_dec = aavso["dec"]

        width, height = self.fitsFileObject.get_fits_image_dimensions()

        # example of another way to get x,y
        # from astropy.coordinates import SkyCoord
        # hdulist = fits.open(first_fits_file)
        # wcs = WCS(hdulist[0].header)
        # if not wcs.has_celestial:
        #     raise ValueError("WCS should contain celestial component")
        # # Define the RA and Dec
        # ra = '20h15m22.625s'
        # dec = '65d01m18.57s'
        # # Convert RA and Dec to SkyCoord object
        # sky_coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
        # # Convert SkyCoord to pixel coordinates
        # x, y = sky_coord.to_pixel(wcs)
        # print(x)
        # print(y)

        wcs_header = self.fitsFileObject.get_fits_header()
        if not WCS(wcs_header).has_celestial:
            try_again = True
            submission_id = None
            while try_again:
                try:
                    if not submission_id:
                        wcs_header = self.ast.solve_from_image(self.fitsFileObject.first_fits_file,
                                                               submission_id=submission_id)
                    else:
                        wcs_header = self.ast.monitor_submission(submission_id, solve_timeout=120)
                except TimeoutError as e:
                    submission_id = e.args[1]
                else:
                    try_again = False

        if wcs_header:
            print("\n")
            wcs = WCS(wcs_header)

            self.targetarray = []
            self.comparray = []
            self.compmagarray = []

            ra_deg, dec_deg = self.convert_to_decimal_degrees(target_ra, target_dec)
            x, y = wcs.all_world2pix(ra_deg, dec_deg, 0)
            if math.isnan(x) or math.isnan(y) or x < 0 or y < 0 or x > width or y > height:
                print("Unable to get x,y coordinates for target star. Please make sure the first image is acceptable and " + self.starname + " is in the field of view.")
                exit(0)
            self.targetarray.append(int(np.round(x)))
            self.targetarray.append(int(np.round(y)))

            for compstar in aavso["photometry"]:

                try:
                    bands = compstar["bands"]
                    for band in bands:
                        if band["band"] == "V":
                            ra_deg, dec_deg = self.convert_to_decimal_degrees(compstar["ra"], compstar["dec"])
                            x, y = wcs.all_world2pix(ra_deg, dec_deg, 0)
                            if math.isnan(x) or math.isnan(y):
                                continue
                            if int(np.round(x)) > 0 and int(np.round(y)) > 0 and int(np.round(x)) < width and int(
                                    np.round(y)) < height:
                                self.comparray.append([int(np.round(x)), int(np.round(y))])
                                self.compmagarray.append(band["mag"])

                except:
                    continue

            self.comparray = np.array(self.comparray)
            self.compmagarray = np.array(self.compmagarray)
            # print(targetarray)
            # print(comparray)

            initvalue = 0.5
            if not isinstance(magnitude, np.float32):
                magnitude = np.mean(self.compmagarray)
            indexes = np.where((self.compmagarray >= magnitude - initvalue) & (self.compmagarray <= magnitude + initvalue))
            indexes = np.array(indexes[0])
            while len(indexes) < 2:
                initvalue += 0.1
                indexes = np.where((self.compmagarray >= magnitude - initvalue) & (self.compmagarray <= magnitude + initvalue))
                indexes = np.array(indexes[0])
                if initvalue > 5:
                    break

            if len(indexes) >= 2:

                self.comparray = self.comparray[indexes]
                self.comparray = self.comparray.tolist()

                self.compmagarray = self.compmagarray[indexes]
                self.compmagarray = self.compmagarray.tolist()

                indexes_to_remove = self.remove_close_points(self.comparray.copy(), 11)
                if len(self.comparray) - \
                        len(indexes_to_remove) >= 2:
                    self.comparray = [item for i, item in enumerate(self.comparray) if i not in indexes_to_remove]
                    self.compmagarray = [item for i, item in enumerate(self.compmagarray) if i not in indexes_to_remove]

                return self.targetarray, self.comparray, self.compmagarray

            else:
                print("Could not find enough comp stars")
                return None, None

        else:
            print("Could not find enough comp stars (empty header)")
            return None, None
