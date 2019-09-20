import cv2
import sys
import time
import logging
import numexpr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import butter, filtfilt
from sklearn.decomposition import FastICA

# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)


LANDMARK_MAP = {
    "right_cheek": 31,
    "left_cheek": 35
}

class HeartRate(object):
    def __init__(self, **kwargs):
        self.frame_rate = 32
        self.times = []
        self.data_container = []
        self.fft = []
        self.t0 = time.time()
        self.transformer = FastICA(n_components=1)
        self.data = kwargs["data"]

    def get_average(self):
        """
        Gets the average value of the matrix for each frame in the video 
        """
        red_average = []
        for roi in self.data:
            red_average.append(np.array(roi["red_data"]).mean())
        red_average = np.array(red_average)
        return red_average

    def normalize(self, mean, std, array):
        expr = '(array - mean)/std'
        return numexpr.evaluate(expr)
    
    def normalization(self, red_average):
        mean = red_average.mean()
        std = np.std(red_average)
        normalized = self.normalize(mean, std, red_average)
        
        # Remove outliers
        q75, q25 = np.percentile(normalized, [75 ,25])
        iqr = q75 - q25
        lower_outlier = q25 - 1.5*iqr
        upper_outlier = q75 + 1.5*iqr
        print(upper_outlier)
        print(lower_outlier)
        indices = normalized[(normalized < lower_outlier).any() or (normalized > upper_outlier).any()]
        print(indices)
        #normalized = np.where(normalized > upper_outlier, upper_outlier, normalized)
        #normalized = np.where(normalized < lower_outlier, lower_outlier, normalized)

        normalized = normalized[normalized > lower_outlier]
        normalized = normalized[normalized < upper_outlier]
        return normalized

    def get_source(self, red_normal):
        # Drop NaNs and zeros
        indices = red_normal[np.isnan(red_normal).any() or red_normal == 0]
        print(indices)
        '''
        for i in red_normal:
            if red_normal[i] == 0 or np.isnan(red_normal[i]):
                # Check the boundaries
                if i == 0:
                    red_normal[i] = red_normal[i+1]
                elif i == len(red_normal) - 1:
                    red_normal[i] = red_normal[i-1]
                else:
                    red_normal[i] = (red_normal[i-1] + red_normal[i+1])/2
        '''

        #red_normal = red_normal[~np.isnan(red_normal)]
        #red_normal = red_normal[red_normal != 0]
        if len(red_normal) > 0:
            red_source = self.transformer.fit_transform(red_normal.reshape(-1, 1))
            red_source = red_source.reshape(-1, )
        else:
            logging.warning("No data found for this window")
            red_source = []
        return red_source

    def filter(self, source_signal, fs, lowcut, highcut, order):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(3, [low, high], btype="bandpass")
        filtered_signal = filtfilt(b, a, source_signal, axis=0)
        return filtered_signal

    def fourier_transform(self, filtered_signal):
        ft = np.fft.fft(filtered_signal, axis=0)
        ft = np.fft.fftshift(ft)
        freq = np.linspace(-30/2, 30/2, num=len(ft))
        fourier = pd.DataFrame({
            "freq": freq,
            "ft": abs(ft)
        })
        return fourier

    def get_peak_value(self, fourier_signal):
        positive_signal = fourier_signal[fourier_signal["freq"] >= 0]
        max_row = positive_signal.loc[positive_signal["ft"].idxmax()]
        return max_row["freq"]

    def determine_heart_rate(self):
        # Start with just the red channel for right cheek right now
        red_average_signal = self.get_average()

        # Normalize the signal
        normalized_signal = self.normalization(red_average_signal)

        # ICA
        source_signal = self.get_source(normalized_signal)
        if len(source_signal) == 0:
            return "HR Failed"

        # Bandpass filter the signal
        filtered_signal = self.filter(
            source_signal=normalized_signal, 
            fs=32,
            lowcut=0.7, 
            highcut=4,
            order=5
        )
        plt.plot(filtered_signal)
        plt.show()
        plt.clf()
        
        # Get the fourier transform of the signal
        fourier_signal = self.fourier_transform(filtered_signal)

        # Determine peak value
        peak_value = self.get_peak_value(fourier_signal)

        # Add thresholding here

        # Get the heart rate in beats per minute
        heart_rate = peak_value * 60
        
        return heart_rate
    
    def get_average_signal(self):
        return self.get_average()

        