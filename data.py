import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
import calendar
from scipy import signal  
from scipy.optimize import leastsq
import data_utils as du

#### Pressure ####
p, t_p = du.make_monthly_API_requests(stationID,yearstart,yearend,air_pressure)

#### Water Level ####
h, t_h = du.make_yearly_API_requests(stationID,yearstart,yearend,hourly_height)


#### Clean data ####
t_datetime, t_timestamp, pressure, water_level = du.interp_over_pressure_waterlevel(p, t_p, h, t_h)

#### Fitting tidal component ####
water_level_average = []
windowwidth = .2  #  in days
# i = 0
for time in t_datetime:
    window_lowerlimit = time - dt.timedelta(days=0.5 * windowwidth)
    window_upperlimit = time + dt.timedelta(days=0.5 * windowwidth)
    ind_window = np.where((t_datetime >= window_lowerlimit) & (t_datetime <= window_upperlimit))[0]
    water_level_average.append(np.average(water_level[ind_window]))

water_level_average = np.array(water_level_average)

#### Pressure and Water Level Correlation ####
pressure_waterlevel_corrcoef = np.corrcoef(pressure,water_level)[0][1]
print("Pressure and Water Level Correlation: {}".format(pressure_waterlevel_corrcoef))


#### Fourier stuff ####
sp_water_level = np.fft.fft(water_level)
sp_water_level_fit = np.fft.fft(water_level_average)
freq = np.fft.fftfreq(t_timestamp.shape[0],d=1.0)

#### Exceedence Probability #####
water_level_sorted = np.sort(water_level)
water_level_rank = np.arange(len(water_level_sorted))
water_level_normalized_rank = (1.0*water_level_rank)/len(water_level_sorted)

exceedenceproball = [1-n for n in water_level_normalized_rank]

##########################################################################################
######################################## Graphing ########################################
##########################################################################################

# air pressure
autoTicks = mdates.AutoDateLocator()
autoFmt = mdates.AutoDateFormatter(autoTicks)
fig = plt.figure(figsize=(20,10))
ax1 = fig.add_subplot(511)
ax1.plot(mdates.date2num(t_datetime),pressure,color='r')
ax1.set_ylabel('Pressure')
ax1.xaxis.set_major_locator(autoTicks)
ax1.xaxis.set_major_formatter(autoFmt)

# water level
ax2 = fig.add_subplot(512)
ax2.plot(mdates.date2num(t_datetime),water_level,color='r')
ax2.plot(mdates.date2num(t_datetime),water_level_average,color='black',linewidth=2.0) #tidal
ax2.set_ylabel('Water Level')
ax2.xaxis.set_major_locator(autoTicks)
ax2.xaxis.set_major_formatter(autoFmt)

# water level - tidal component
ax3 = fig.add_subplot(513)
ax3.plot(mdates.date2num(t_datetime),water_level - water_level_average,color='r')
ax3.set_ylabel('Residual')
ax3.xaxis.set_major_locator(autoTicks)
ax3.xaxis.set_major_formatter(autoFmt)

# water level - tidal component
ax4 = fig.add_subplot(514)
ax4.plot(freq[1:int(len(freq)/2)],np.abs(sp_water_level[1:int(len(sp_water_level)/2)]),color='black')
ax4.plot(freq[1:int(len(freq)/2)],np.abs(sp_water_level_fit [1:int(len(sp_water_level_fit)/2)]),color='red')
ax4.legend(['Original Data','Fit Data'],loc=0)
ax4.set_ylabel('Signal Analysis')

# water level - tidal component
ax5 = fig.add_subplot(515)
ax5.plot(water_level_sorted,exceedenceproball)
ax5.set_ylabel('Exceedence')

plt.show()
