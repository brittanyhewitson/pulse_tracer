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
        self.frame_rate = 30
        self.times = []
        self.data_container = []
        self.fft = []
        self.t0 = time.time()
        self.transformer = FastICA(n_components=1)
        self.data = kwargs["data"]

    def get_average(self):
        
        red_average = []
        for roi in self.data:
            red_average.append(np.array(roi["red_data"]).mean())
        
        red_average = np.array(red_average)
        
        '''
        plt.plot(red_average)
        plt.show()
        plt.clf()
        '''
        return red_average

    def normalize(self, mean, std, array):
        expr = '(array - mean)/std'
        return numexpr.evaluate(expr)
    
    def normalization(self, red_average):
        mean = red_average.mean()
        std = np.std(red_average)
        normalized = self.normalize(mean, std, red_average)

        return normalized

    def get_source(self, red_normal):
        red_source = self.transformer.fit_transform(red_normal.reshape(-1, 1))
        '''
        plt.plot(red_source)
        plt.show()
        plt.clf()
        '''
        return red_source

    def filter(self, source_signal, fs, lowcut, highcut, order):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        b, a = butter(3, [low, high], btype="bandpass")
        filtered_signal = filtfilt(b, a, source_signal, axis=0)
        '''
        plt.plot(filtered_signal)
        plt.show()
        plt.clf()
        '''
        return filtered_signal

    def fourier_transform(self, filtered_signal):
        ft = np.fft.fft(filtered_signal, axis=0)
        ft = np.fft.fftshift(ft)
        freq = np.linspace(-30/2, 30/2, num=len(ft))
        '''
        plt.plot(freq, abs(ft))
        plt.show()
        '''
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

        # Bandpass filter the signal
        filtered_signal = self.filter(
            source_signal=normalized_signal, 
            fs=30,
            lowcut=0.7, 
            highcut=4,
            order=5
        )

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

        