from astropy.io import fits
import os
from datetime import datetime
import matplotlib.pyplot as plt
from astropy.visualization import (MinMaxInterval, SqrtStretch, LinearStretch, AsinhStretch, HistEqStretch, LogStretch, ImageNormalize, AsymmetricPercentileInterval)

class FitsFile:
    def __init__(self, config):

        self.config = config

        self.first_fits_file = None

    def find_first_gz_file(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith('.gz'):
                self.first_fits_file = os.path.join(directory, filename)
                return self.first_fits_file
        return None

    def get_observation_date(self):
        date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        header = self.get_fits_header()

        observation_date = header.get('DATE-OBS')
        observation_date = datetime.strptime(observation_date, date_format)
        return observation_date.strftime("%Y-%m-%d")

    def get_fits_header(self):
        with fits.open(self.first_fits_file) as hdul:
            try:
                header = hdul.header
            except:
                header = hdul[0].header
            return header

    def get_fits_image_dimensions(self):
        with fits.open(self.first_fits_file) as hdul:
            try:
                data = hdul.data
            except:
                data = hdul[0].data
            height, width = data.shape
            return width, height

    def convert_fits_to_png_with_markers(self, output_png, coordinates, colors, starname):
        # Set the backend to Agg

        plt.switch_backend('Agg')
        hdu_list = fits.open(self.first_fits_file)
        image_data = hdu_list[0].data
        height, width = image_data.shape
        hdu_list.close()

        # Create a figure and axis
        fig, ax = plt.subplots()

        # norm = ImageNormalize(image_data, interval=MinMaxInterval(), stretch=HistEqStretch(image_data))
        norm = ImageNormalize(image_data, interval=AsymmetricPercentileInterval(80,99), stretch=LinearStretch())

        plt.title(starname)

        # Add dummy plots for the legend
        plt.plot([], [], 'g+', label='Target Star')
        plt.plot([], [], 'r+', label='Comp Stars')
        plt.legend(loc='upper right', frameon=True, shadow=True,
                   facecolor='lightgrey', bbox_to_anchor=(1.15, 1.15))

        # Display the FITS image data
        plt.imshow(image_data, norm=norm, origin='lower', cmap='gray_r')

        # Draw horizontal and vertical lines every 100 pixels
        for y in range(0, height, 100):
            plt.axhline(y=y, color='grey', linestyle='--', alpha=0.75, linewidth=0.5)
        for x in range(0, width, 100):
            plt.axvline(x=x, color='grey', linestyle='--', alpha=0.75, linewidth=0.5)

        # Draw plus markers at the specified coordinates with different colors
        for (x, y), color in zip(coordinates, colors):
            ax.plot(x, y, marker='+', color=color, markersize=20, markeredgewidth=0.5, alpha=1.0)

        # Save the figure as a PNG file
        plt.savefig(output_png)
        plt.close()
