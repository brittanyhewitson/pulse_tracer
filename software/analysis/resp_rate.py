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
        
        # find peaks
        peaks = sc.signal.find_peaks(self.avg_sig,height=0)
        
        # interpolate between peaks to find envelope
        model = sc.interpolate.interp1d(peaks[0],peaks[1]['peak_heights'], kind = 'cubic',bounds_error = False, fill_value=0.0)
        self.resp_sig = [model(x) for x in range(len(self.avg_sig))]
        #self.avg_sig = sc.signal.hilbert(self.avg_sig)
        
        # calculate respiratory rate
        breath_num = len(sc.signal.find_peaks(self.resp_sig))
        breath_per_min = breath_num/(len(self.resp_sig)/(30*60))
    
        #plt.plot(self.avg_sig)
        #plt.plot(self.resp_sig)
        #plt.plot(self.resp_sig["freq"], self.resp_sig["ft"])
        #plt.show()
        
        return breath_per_min


"""
#### Bandpassfilter to filter out required frequencies for Heart Rate from PPG data
from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


##RESPIRATION RATE

# Filter requirements.
lowcut1 = 0.4
highcut1 = 0.7
fs3= 30
order3 = 3

# Filter the data, and plot both the original and filtered signals.
rr =butter_bandpass_filter(u, lowcut1, highcut1, fs, order3)
plt.figure(4)
plt.plot(t, u, color ='crimson', label='data')
plt.plot(t, rr, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.ylabel('PPG data')
plt.title('Bandpass Filtered Data for Respiration rate detection')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()

##Periodogram 2
FFT3 = abs(sc.fft(rr,N))
f3 = 20*sc.log10(FFT3)
f3 = f3[range(N/2)]   #remove mirrored part of FFT
freqs3 = sc.fftpack.fftfreq(N, t[1]-t[0])
freqs3 = freqs3[range(N/2)]   #remove mirrored part of FFT



##calculate respiration rate

## Remove maximum PSD because it is at 0 Hz.
## Find best frequency
new = np.array(f3).tolist()
new.remove(max(new))
m3 = max(f3)
d3 =[i for i, j in enumerate(f3) if j == m3] ## the sample number associated to maximum PSD


##Plotting Periodogram 2
x2 = freqs3[d3]
y2 = m3
plt.figure(5)
plt.subplot(2,1,1)
plt.plot(freqs3, f3,linewidth = 2.5,color='firebrick')
plt.ylabel("PSD")
plt.title('Periodogram for Respiration Rate detection')
plt.grid()
plt.subplot(2,1,2)
plt.plot(freqs3, f3,linewidth = 2.5,color='darkolivegreen')
plt.xlim((0,2))
plt.ylim((0,y2+20))
plt.text(x2,y2,'*Peak corresponding to Best Frequency')
plt.grid()
plt.show()

## Print PSD and Frequency
print 'Maximum PSD for best frequency' , m3
print "Frequency corresponding to maximum PSD", freqs3[d3], "Hz"

#Calculate Respiration Rate
RespRate = freqs3[d3]*60

#print "Respiration Rate =", RespRate
print "Respiration Rate  =", RespRate, "Breaths per minute" 
#test"""