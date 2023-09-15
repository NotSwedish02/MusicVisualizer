from scipy.io import wavfile
import numpy as np
import pygame as py
from scipy.fft import fft, fftfreq
import matplotlib
from matplotlib import pyplot as plt
import math
import librosa


VALUES_PER_SECOND = 20
FPS = 60

DELTA = VALUES_PER_SECOND/FPS


class Visualizer():
    def __init__(self, song):
        self.song = song
        self.samplerate, data = wavfile.read(song)


        #Debug - show samplerate
        #print(samplerate)

        self.duration_in_sec = librosa.get_duration(filename=song)


    
        try:
            _, self.num_of_channels = data.shape
        except:
            self.num_of_channels = 1

        if self.num_of_channels == 1:
            self.ydata_for_line = list(data)
            ydata = list(np.array_split(data, VALUES_PER_SECOND * self.duration_in_sec))

        else:
            self.ydata_for_line = list(data[:,0])
            ydata = list(np.array_split(data[:,1], VALUES_PER_SECOND * self.duration_in_sec))


        self.start = 0
        self.y_origin = 500


        #Lists for x and y axi of frequency display
        self.xf_list = []
        self.yf_list = []

        #Getting the frequency spectrum
        for data in ydata:
            normalized_data = np.int16((data / data.max()) * 32767)
            N = data.size

            yf = list(np.abs(fft(normalized_data)))
            xf = list(fftfreq(N, 1 / self.samplerate))

            self.xf_list.append(xf)
            self.yf_list.append(yf)


        #Debug - show frequency spectrum of an instant (0), on a plot
        #plt.plot(np.resize(xf_list[0],15031), np.abs(yf_list[0]))
        #plt.show()

        #Debug - Show frequency range
        #print(len(xf_list))


        py.init()
        py.mixer.init(self.samplerate, -16, 1, 1024)

        self.screen = py.display.set_mode((600,600))

        self.clock = py.time.Clock()


        py.mixer.music.load(song)
    def run(self):
        self.count = 0

        self.run = True

        while self.run:
            self.screen.fill((0,0,0))

            for e in py.event.get():
                if e.type == py.QUIT:
                    self.run = False


            #Frame count to move the visualization at the same rate the song plays
            self.count += DELTA
            
            #Get x and y axi of the specturm for the current instant
            xf, yf = self.xf_list[int(self.count)], self.yf_list[int(self.count)]

            #Drawing the raw data in points
            '''for i in range(1000):
                py.draw.circle(self.screen, (255,255,255), (10+xf[i]/40, 300-yf[i]/30000), 1)'''

            #Drawing the raw data in points, as polygon
            points = [(10+xf[i]/40, 300-yf[i]/30000) for i in range(1000)]
            points.append((max(xf)/40, 300))
            points.append((0,300))

            py.draw.polygon(self.screen, (100,100,255), points)


            #Drawing the bars, which each are the average of five points
            for i in range(200):
                val = 0
                for j in range(5):
                    val += yf[i+j]/30000
                val/=5
                py.draw.line(self.screen, (255,255,255), (10+xf[i]/8, 200-val), (10+xf[i]/8, 200), 2)

            #Drawing the bars but in a circle
            for i in range(200):
                val = 0
                for j in range(5):
                    val += yf[i+j]/30000
                val/=5

                ag = xf[i] * math.pi / 2000 

                module_ = val

                py.draw.line(self.screen, (255,255,255), (300+math.cos(ag)*50,400+ math.sin(ag)*50), 
                                (300+math.cos(ag)*(50+val), 400+math.sin(ag)*(50+val)), 1)
                

            #Drawing the sound line
            self.start += int(self.samplerate/600)

            last_pos = (0,0)
            for i in range(1000):
                pos = (i*6, self.y_origin - self.ydata_for_line[(i+self.start)*10]/400) #pos_y is every 10th value, divided by 90 to fit
                py.draw.line(self.screen, (255,255,255), pos, last_pos, 1)

                last_pos = pos

            #Only start playing the song after the first display is done, so its synced
            if not py.mixer.music.get_busy():
                py.mixer.music.play()

            self.clock.tick(FPS)
            py.display.set_caption("FPS: " + str(int(self.clock.get_fps())))
            py.display.update()

viz = Visualizer("Songs/telepatia.wav")
viz.run()