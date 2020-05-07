import numpy as np
import pickle
from scipy.io.wavfile import read
from scipy import signal

# dimensions of room. Should be consistent with values present in realtime.py
x_dim = 30
y_dim = 20


# Schroeder reverberator
def reverbmaker(buffer, x_pos, y_pos, sr):
    # delays along x-axis
    delay_dist_1 = x_dim - (2 * abs(x_pos))
    delay_dist_2 = x_dim + (2 * abs(x_pos))
    # delays along y-axis
    delay_dist_3 = y_dim - (2 * abs(y_pos))
    delay_dist_4 = y_dim + (2 * abs(y_pos))
                                    
    # Build a Schroeder reverberator
    # COMB 1
    delay = int((delay_dist_1 / 343) * sr)
    filt_coef = np.zeros(delay)
    filt_coef[0] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef_rec[-1] = 0.4

    comb_out1 = signal.lfilter(filt_coef, filt_coef_rec, buffer)

    # COMB 2
    delay = int((delay_dist_2 / 343) * sr)
    filt_coef = np.zeros(delay)
    filt_coef[0] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef_rec[-1] = 0.4

    comb_out2 = signal.lfilter(filt_coef, filt_coef_rec, buffer)

    # COMB 3
    delay = int((delay_dist_3 / 343) * sr)
    filt_coef = np.zeros(delay)
    filt_coef[0] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef_rec[-1] = 0.4

    comb_out3 = signal.lfilter(filt_coef, filt_coef_rec, buffer)

    # COMB 4
    delay = int((delay_dist_4 / 343) * sr)
    filt_coef = np.zeros(delay)
    filt_coef[0] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef_rec[-1] = 0.4

    comb_out4 = signal.lfilter(filt_coef, filt_coef_rec, buffer)

    # Add up comb filters
    comb_out = comb_out1 + comb_out2 + comb_out3 + comb_out4

    # ALLPASS 1
    delay = int((delay_dist_1 / 343) * sr)   
    filt_coef = np.zeros(delay)
    filt_coef[0] = 0.3
    filt_coef[-1] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef[-1] = -0.3

    allpass_out1 = signal.lfilter(filt_coef, filt_coef_rec, comb_out)

    # ALLPASS 2
    delay = int((delay_dist_3 / 343) * sr) 
    filt_coef = np.zeros(delay)
    filt_coef[0] = 0.3
    filt_coef[-1] = 1

    filt_coef_rec = np.zeros(delay)
    filt_coef_rec[0] = 1
    filt_coef[-1] = -0.3

    allpass_out2 = signal.lfilter(filt_coef, filt_coef_rec, allpass_out1)

    # SCHROEDER
    final = (1.3*buffer) + allpass_out2
    
    return(final)


# retrieve 10-second snippet of song
sr, x = read("balloons.wav")
to_filter = x[32*sr:42*sr]

# build dictionary of reverbed snippet for every possible location in room
x_max = x_dim / 2
y_max = y_dim / 2

x_pos = 0.0
y_pos = 0.0

reverbs = {}
while x_pos < x_max:
    reverbs[str(x_pos)] = {}

    while y_pos < y_max:
        reverbs[str(x_pos)][str(y_pos)] = reverbmaker(to_filter, x_pos, y_pos, sr)
        print("Reverbed x_pos: " + str(x_pos) + " | y_pos: " + str(y_pos))
        y_pos += 0.5

    y_pos = 0.0
    x_pos += 0.5

reverb_file = open('reverbs.pkl', 'wb')
pickle.dump(reverbs, reverb_file)
reverb_file.close()
    
