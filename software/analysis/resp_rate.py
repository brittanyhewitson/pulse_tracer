import scipy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class RespRate(object):
    def __init__(self, **kwargs):
        self.avg_sig = []
        self.resp_sig = []
        
    def bandpass(self, sig, fs, lowcut, highcut):
        lct = lowcut/(0.5 * fs)
        hct = highcut/(0.5 * fs)

        b, a = sc.signal.butter(5, [lct, hct], btype="bandpass")
        return sc.signal.filtfilt(b, a, sig)
    
        
    def determine_resp_rate(self,data):
        # filter
        self.avg_sig = self.bandpass(data,30,0.067,1)
        
        self.avg_sig = sc.signal.savgol_filter(self.avg_sig,11,1)
        
        try:
            # find peaks
            peaks = sc.signal.find_peaks(self.avg_sig,height=0)
            
            # interpolate between peaks to find envelope
            model = sc.interpolate.interp1d(peaks[0],peaks[1]['peak_heights'], kind = 'cubic',bounds_error = False, fill_value=0.0)
            self.resp_sig = [model(x) for x in range(len(self.avg_sig))]
            #self.avg_sig = sc.signal.hilbert(self.avg_sig)
            
            # calculate respiratory rate
            breath_num = len(sc.signal.find_peaks(self.resp_sig))
            breath_per_min = breath_num/(len(self.resp_sig)/(30*60))
        except:
            return "<RR Failed>"
        
        return breath_per_min