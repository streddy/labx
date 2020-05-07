import numpy as np
import pyaudio
import wave
import matplotlib.pyplot as plt
import pickle
from threading import Thread
from matplotlib.widgets import Slider, Button

# The current location of the listener and sound source within the room
x_val = 0.0
y_val = 0.0

# Dimensions of the room
# If changed, need to recompile reverb dictionary in makereverb.py
x_dim = 30
y_dim = 20
    
# Pre-calculated reverbs from each position within the room
# Will take a few seconds to load into memory
reverbs = pickle.load(open('reverbs.pkl', 'rb'))


# Play and spatialize 10-second snippet. Should be spawned in a new Thread
def playsong():
    global x_val
    global y_val

    # Create PyAudio stream
    p = pyaudio.PyAudio()
    
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 44100,
                    output = True)

    blocksize = 1024
    
    # Loop through snippet and write to output stream
    start = 0
    for n in range(int(44100*20/blocksize)):
        stop = start + blocksize
        
        # Get reverbed sample corresponding to current room position and timestamp
        # Convert to PyAudio writeable format
        stream.write((reverbs[str(abs(x_val))][str(abs(y_val))][start:stop] / 2).astype(np.int16).tostring())
        start = stop

    stream.close()
    p.terminate()


# Create GUI
def plotroom(x_dim, y_dim):
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25, bottom=0.25)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
                                
    x1 = x_dim / 2.0
    x2 = -1.0 * x1
                                            
    y1 = y_dim / 2.0
    y2 = -1.0 * y1
                
    # Plot "room" and initial listener/source location
    plt.plot([x1, x2], [y1, y1], color='blue', linewidth=4)
    plt.plot([x1, x2], [y2, y2], color='blue', linewidth=4)
    plt.plot([x1, x1], [y1, y2], color='blue', linewidth=4)
    plt.plot([x2, x2], [y1, y2], color='blue', linewidth=4)
    listener, = plt.plot(0, 0, 'bo')

    # Sliders to move listener/source position within room
    axcolor = 'lightgoldenrodyellow'
    ax_x = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
    ax_y = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)

    x_slider = Slider(ax_x, 'X Position', x2 + 0.5, x1 - 0.5, valinit=0, valstep=0.5)
    y_slider = Slider(ax_y, 'Y Position', y2 + 0.5, y1 - 0.5, valinit=0, valstep=0.5)

    # Update global listener/source position upon slider move
    # Redraw listener/source position on plot
    def update(val):
        global x_val
        global y_val
        x_val = x_slider.val
        y_val = y_slider.val
        listener.set_xdata(x_val)
        listener.set_ydata(y_val)
        fig.canvas.draw_idle()

    x_slider.on_changed(update)
    y_slider.on_changed(update)

    # Button to replay song snippet
    ax_b = plt.axes([0.025, 0.5, 0.15, 0.15])
    b_replay = Button(ax_b, 'Replay', color=axcolor, hovercolor='0.975')

    # Spawn new Thread to play snippet
    def replay(event):
        Thread(target=playsong).start()
    b_replay.on_clicked(replay)
            
    plt.suptitle("Listener and Source Position Within a " + str(x_dim) + "m x " + str(y_dim) + "m Room")
    plt.show()

    return(x_slider, y_slider)


Thread(target=playsong).start()
plotroom(x_dim, y_dim)
