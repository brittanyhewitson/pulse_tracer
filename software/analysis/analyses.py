import cv2
import sys
import time
import logging
import numexpr

import scipy as scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np

from scipy.signal import butter, filtfilt
from sklearn.decomposition import FastICA

import sq_stft_utils as sq


# Set up logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, stream=sys.stderr, level=logging.INFO)

ROI_MAP = {
    "31":"right_cheek",
    "35":"left_cheek",
    "27":"upper_nose",
    "28":"mid_upper_nose",
    "29":"mid_lower_nose",
    "30":"lower_nose",
    "17":"left_outer_brow",
    "18":"left_mid_outer_brow",
    "19":"left_mid_brow",
    "20":"left_mid_inner_brow",
    "21":"left_inner_brow",
    "22":"right_inner_brow",
    "23":"right_mid_inner_brow",
    "24":"right_mid_brow",
    "25":"right_mid_outer_brow",
    "26":"right_outer_brow",
    "99":"full_face"
}


class MatrixAnalysis(object):
    def __init__(self, **kwargs):
        self.frame_rate = 30
        self.data = kwargs["data"]
        self.prior_bpm = 90

    def reorder_data(self):
        """
        """
        # Organize data by the ROI Location
        roi_data = {}
        for roi in self.data:
            # Data is a list of dictionaries
            location_id = ROI_MAP[str(roi["location_id"])]
            try:
                roi_data[location_id].append(roi["red_data"])
            except KeyError:
                roi_data[location_id] = []
                roi_data[location_id].append(roi["red_data"])

        ppg_data=np.array([np.array(xi) for key, xi in roi_data.items()])
        ppg_data = ppg_data.astype(int)

        for i in range(ppg_data.shape[0]):
            q75, q25 = np.percentile(ppg_data[i, :], [75 ,25])
            iqr = q75 - q25
            lower_outlier = q25 - 1.5*iqr
            upper_outlier = q75 + 1.5*iqr
            mean_value = ppg_data[i, :].mean()

            for n in range(ppg_data.shape[1]):
                if ppg_data[i, n] > upper_outlier or ppg_data[i, n] < lower_outlier:
                    ppg_data[i, n] = mean_value

        self.ppg_data = ppg_data

    def butter_hpf(self, signal, lowcut, order):
        """
        """
        nyq = 0.5 * self.frame_rate
        low = lowcut / nyq
        
        b, a = butter(order, low, btype="highpass")
        filtered_signal = scipy.signal.filtfilt(b, a, signal, axis=1)
        return filtered_signal

    def butter_bandpass(self, signal, lowcut, highcut, order):
        nyq = 0.5 * self.frame_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        filtered_signal = scipy.signal.filtfilt(b, a, signal)
        return filtered_signal

    def svd(self, filtered_signal):
        """
        """
        U, s, V = np.linalg.svd(filtered_signal, full_matrices=False)
        return U, s, V

    def eigenvector_quality(self, signals, prior_bpm, fs, window, fL, fH, fp_d, fp_u, verbose=False):
        """
        """
        nv = signals.shape[0]
        quality_array = np.zeros([nv])
        for i in np.arange(nv):
            senal = signals[i,:]

            filtered_signal = self.butter_bandpass(
                senal,
                lowcut=fL,
                highcut=fH,
                order=5
            )
            
            t_v = np.arange(filtered_signal.shape[0])/self.frame_rate

            stft_v, f_v,_,_= sq.SST_helper(filtered_signal, self.frame_rate, fH/self.frame_rate, fL/self.frame_rate, windowLength=window)

            f_v = f_v*self.frame_rate
            nu = np.argmin(np.abs(f_v-fp_u))
            nd = np.argmin(np.abs(f_v-fp_d))
            stft_vp = np.abs(stft_v[nd:nu,:])
            stft_vp = stft_vp[::-1,:]
            
            ## Quality index ##
            prior_f = self.prior_bpm/60
            f_low_prior = prior_f*0.75
            f_high_prior = prior_f*1.25
            idx_prior = np.logical_and(f_v>f_low_prior,f_v<f_high_prior)
            idx_band = np.logical_and(f_v>0.25*prior_f,f_v<2*prior_f)

            power= np.abs(stft_v).sum(1)
            power_fraction = power[idx_prior].sum()/power[idx_band].sum()
            quality_array[i] = power_fraction
            
            
            print('Signal :: ' + str(i))
            print('Power fraction', power_fraction)
            if verbose:
                
                #Plot Signals
                plt.figure(figsize = (12,5))
                plt.subplot(2,1,1)
                plt.plot(t_v,filtered_signal)
                plt.xlim([t_v[0],t_v[-1]])
                plt.subplot(2,1,2)
                plt.imshow(stft_vp,extent=[t_v[0], t_v[-1],f_v[nd]*60,f_v[nu]*60],
                        aspect = 'auto',cmap='Blues')
                plt.xlabel('Time [s]')
                plt.ylabel('Frequency [bpm]')
                plt.show()

        return quality_array

    def preprocess_data(self):
        """
        """
        self.reorder_data()

        # Filter the data
        filtered_signal = self.butter_hpf(self.ppg_data, lowcut=0.4, order=5)

        # SVD
        U, s, V = self.svd(filtered_signal)

        # Calculate Eigenvector Quality
        num_v = np.minimum(40, V.shape[0])
        quality_array = self.eigenvector_quality(
            V[0:num_v, :],
            self.prior_bpm,
            self.frame_rate,
            window=301,
            fL=0.4,
            fH=5,
            fp_d=0.5,
            fp_u=5
        )

        Vc = np.array(V[np.argsort(quality_array)[::-1],:]) #sort vectors by best quality
        Vc = np.cumsum(Vc,axis = 0) #cumulate
        quality_cum_array = self.eigenvector_quality(
                Vc,
                self.prior_bpm,
                self.prior_bpm,
                window = 301,
                fL=0.4,
                fH=5, 
                fp_d=0.5,
                fp_u=5,
                verbose=False
            )

        ix_qual = np.argmax(quality_cum_array)
        fL = 0.4
        fH = 5

        # GET BEST SIGNAL & COMPUTE STFT #
        senal = Vc[ix_qual,:]
        filtered_signal = self.butter_bandpass(senal, fL, fH, order=5)
        t_v = np.arange(filtered_signal.shape[0])/self.frame_rate
        stft_v, f_v,_,_= sq.SST_helper(filtered_signal, self.frame_rate, fH/self.frame_rate, fL/self.frame_rate, windowLength=301)

        # Range of frequencies to plot
        f_v = f_v*self.frame_rate
        fp_u = 4
        fp_d = 0.5
        nu = np.argmin(np.abs(f_v-fp_u))
        nd = np.argmin(np.abs(f_v-fp_d))
        stft_vp = np.abs(stft_v[nd:nu,:])
        stft_vp = stft_vp[::-1,:]

        # Plot Extracted Signal
        nt_i =0
        nt_f = 1200
        plt.plot(t_v[nt_i:nt_f],filtered_signal[nt_i:nt_f]*-1,linewidth = 3)
        plt.subplot(2,1,1)
        plt.title('Extracted Signal',fontsize = 25)
        plt.ylabel('A.U.',fontsize = 25)
        plt.yticks([-0.05,0,0.05])
        plt.xticks([0,5,10,15,20,25,30])
        ax = plt.gca()
        ax.set_facecolor((1.0, 1, 1))
        plt.grid('on',color = 'gray')
        plt.show()
        plt.clf()

        self.ppg_data = filtered_signal

    def get_hr(self):
        """
        """
        self.preprocess_data()

        ft = np.fft.fft(self.ppg_data, axis=0)
        ft = np.fft.fftshift(ft)
        freq = np.linspace(-self.frame_rate/2, self.frame_rate/2, num=len(ft))
        fourier = pd.DataFrame({
            "freq": freq,
            "ft": abs(ft)
        })
        plt.plot(fourier["freq"], fourier["ft"])
        plt.show()
        plt.clf()
        positive_signal = fourier[fourier["freq"] >= 0]
        max_row = positive_signal.loc[positive_signal["ft"].idxmax()]
        peak_value = max_row["freq"]

        heart_rate = peak_value * 60

        return heart_rate

    def get_rr(self):
        """
        """
        # TODO
        return "TODO"



class FDAnalysis(object):
    """
    """
    def __init__(self, **kwargs):
        self.frame_rate = 30
        self.data = kwargs["data"]
        self.ica_transformer = FastICA(n_components=1)

    def get_average(self):
        """
        Gets the average value of the ROI for each frame in the video
        """
        red_average = []
        for roi in self.data:
            red_average.append(np.array(roi["red_data"]).mean())
        red_average = np.array(red_average)
        return red_average

    def normalize(self, mean, std, array):
        """
        """
        expr = '(array - mean)/std'
        return numexpr.evaluate(expr)
    
    def normalization(self, red_average):
        """
        """
        mean = red_average.mean()
        std = np.std(red_average)
        normalized = self.normalize(mean, std, red_average)
        
        # Remove outliers, NaNs and 0's
        q75, q25 = np.percentile(normalized, [75 ,25])
        iqr = q75 - q25
        lower_outlier = q25 - 1.5*iqr
        upper_outlier = q75 + 1.5*iqr
        mean_value = normalized.mean()
        for i in range(normalized.shape[0]):
            if normalized[i] > upper_outlier or normalized[i] < lower_outlier:
                normalized[i] = mean_value

        normalized = normalized[normalized > lower_outlier]
        normalized = normalized[normalized < upper_outlier]
        return normalized

    def get_source(self, red_normal):
        """
        """
        #red_normal = red_normal[~np.isnan(red_normal)]
        #red_normal = red_normal[red_normal != 0]
        if len(red_normal) > 0:
            red_source = self.ica_transformer.fit_transform(red_normal.reshape(-1, 1))
            red_source = red_source.reshape(-1, )
        else:
            logging.warning("No data found for this window")
            red_source = []
        return red_source

    def filter(self, source_signal, lowcut, highcut, order):
        """
        """
        nyq = 0.5 * self.frame_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(3, [low, high], btype="bandpass")
        filtered_signal = filtfilt(b, a, source_signal, axis=0)
        self.ppg_data = filtered_signal

    def fourier_transform(self, filtered_signal):
        """
        """
        ft = np.fft.fft(filtered_signal, axis=0)
        ft = np.fft.fftshift(ft)
        freq = np.linspace(-self.frame_rate/2, self.frame_rate/2, num=len(ft))
        fourier = pd.DataFrame({
            "freq": freq,
            "ft": abs(ft)
        })
        return fourier

    def get_peak_value(self, fourier_signal):
        """
        """
        positive_signal = fourier_signal[fourier_signal["freq"] >= 0]
        max_row = positive_signal.loc[positive_signal["ft"].idxmax()]
        return max_row["freq"]

    def get_hr(self):
        """
        """
        # Start with just the red channel for right cheek right now
        red_average_signal = self.get_average()

        # Normalize the signal
        normalized_signal = self.normalization(red_average_signal)

        # ICA
        source_signal = self.get_source(normalized_signal)
        if len(source_signal) == 0:
            return "HR Failed"

        # Bandpass filter the signal
        self.filter(
            source_signal=normalized_signal, 
            lowcut=0.7, 
            highcut=4,
            order=5
        )
        plt.plot(self.ppg_data)
        plt.show()
        plt.clf()
        
        # Get the fourier transform of the signal
        fourier_signal = self.fourier_transform(self.ppg_data)

        # Determine peak value
        peak_value = self.get_peak_value(fourier_signal)

        # Add thresholding here

        # Get the heart rate in beats per minute
        heart_rate = peak_value * 60
        
        return heart_rate

    # TODO: Add Corey's RR algorithm here
    def get_rr(self):
        return "TODO"
