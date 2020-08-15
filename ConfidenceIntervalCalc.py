#Copyright Sorensenc 2020 - resume.conneris.me

import sys
import matplotlib.pyplot as plt
import math
from collections import Counter
import statistics

'''
In the section below, edit the Observations (Obs) list to reflect your team's velocity observations.
Sometimes, things go awry and result in an observation not being representational of the team's expected performance.
This script refers to those observations as "Invalid Observations"
It's good to record ALL observations; even if they're invalid. 
To indicate an observation is invalid, mark it as negative.

*** Invalid observations of 0 are not supported; use -0.01 instead of -0 ***

These negative/invalid observations will be tracked and plotted, however they will be ignored during all calculations of the Confidence Interval and Mean
Some examples of causes for invalid velocity observations may include, but not limited to:
    > abnormally high amount of vacation time taken by the team (Christmas, Diwali, etc.),
    > team member(s) unavailable (hospitalized, vacation, maternity leave, etc.)
    > Sprint was cancelled
    > Team composition was modified i.e. team member(s) added/removed
    > Death-March performance (i.e. unsustainable pace) was demanded from the team for go-live/break-fix
'''

''' --- Edit Velocity Observations Below! --- '''
#Observations should be in chronological order, and if any observations are invalid, or unfair, mark their value as a negative number (Note: use -0.01 instead of -0). 
Obs = [-22, -53, 28, 19, 32, 5, 20, -2, 20, 20, 25, 36, 37, 36, 5, 29, 45, 24, 23]
''' --- Edit Velocity Observations Above! --- '''


###---                     ---###
###--- Calculation Methods ---###
###---                     ---###


#Collect all the valid observations up-to-and-including current observation
def ValObs(i): return [o for o in Obs[:i + 1] if o >= 0]

#Collect all the valid observations up-to-and-including current observation and sort by ascending value
def ValObsSorted(i): return sorted(ValObs(i))

#calculate the mean of given range
def Mean(range): return int(sum(range)/len(range))

#Given the (n)umber of observations, calculate the Lower 90% Confidence Interval Index (CII) number (rounding up to nearest whole number for list indexing)
def LowerCII(n): return int((math.ceil((float(n)/2.0) - (1.645 * (float(n)*0.25) ** 0.5))) - 1)

#Given the (n)umber of observations, calculate the Upper 90% Confidence Interval Index (CII) number (rounding up to nearest whole number for list indexing)
def UpperCII(n): return int((math.ceil((float(n)/2.0) + (1.645 * (float(n)*0.25) ** 0.5))) - 1)

#for i, i in enumerate(range(1,10)): print(i, LowerCII(i), UpperCII(i)) #Generates commented output below
'''
Until the 7th valid velocity observation (i.e. n=7), the 90% Confidence Interval (zero-based) Indexes (CII) practically include all valid velocity observations:
    n   LowerCII    UpperCII    All Indexes
    1   -1	        1           0
    2	-1	        2           0-1
    3	0	        2           0-2
    4	0	        3           0-3
    5	0	        4           0-4
    6	0	        5           0-5
    7	1	        5           0-6
    8   1           6           0-7
    9   2           6           0-8
'''

#plot best overlap Velocity range/value across all forecasted Confidence Interval ranges
def ShadeOverlap(ax, x):
    if min(yu) - max(yl) >= 0:
        #if there's a range between the lowest high and highest low, or the lowest high and highest low are equal, that is the overlap range
        ax.fill_between(x, [max(yl)] * (len(x)), [min(yu)] * (len(x)), color="gray", alpha=0.2, label="CI Overlap Range")

        #Annotate values of the forecasted 90% Confidence Interval
        ax.annotate("{}".format(min(yu)), xy=(x[-1] - 0.1, min(yu) + 0.6), color="gray", horizontalalignment='right')
        ax.annotate("{}".format(max(yl)), xy=(x[-1] - 0.1, max(yl) - 0.6), color="gray", horizontalalignment='right')
    else:        
        #sort all upper and lower values by ascending order
        yuSorted = sorted(yu)
        ylSorted = sorted(yl)

        #Counters
        i, j = 1, 1

        #start ignoring the "middle" values, starting with the highest low, until there is an overlap
        while True:
            if yuSorted[j] - ylSorted[-i] >= 0: break
            else: 
                if i == j: i += 1
                else: j += 1
        #Shade region within all forecasted Confidence Interval regions
        ax.fill_between(x, [ylSorted[-i]] * (len(x)), [yuSorted[j]] * (len(x)), color="gray", alpha=0.2, label="CI Overlap Range")

        #Annotate values of the forecasted 90% Confidence Interval
        ax.annotate("{}".format(yuSorted[j]), xy=(x[-1] + 0.1, yuSorted[j] + 0.6), color="gray", horizontalalignment='right')
        ax.annotate("{}".format(ylSorted[-i]), xy=(x[-1] + 0.1, ylSorted[-i] - 0.6), color="gray", horizontalalignment='right')
        


###---                 ---###
###--- Data Validation ---###
###---                 ---###    


#if there's no (valid) velocity observations, exit script
if len(Obs) == 0 or len(Obs) - (len(Obs) - len(ValObs(len(Obs) - 1))) == 0: 
    print("No (valid) observations provided for forecasting; exiting forecast!")
    sys.exit()
else: pass


###---               ---###
###--- Prepare Plots ---###
###---               ---###    


#create figure with subplots
fig, (ax1, ax2) = plt.subplots(2)

#condense figure layout
fig.tight_layout()

#Set title of figure's window
fig.canvas.set_window_title("Confidence Intervals & Forecast")

#if there's fewer than 24 velocity observations, then set figure's window height to 6" & width to 7", otherwise set figure's window height to 6" & width to 0.3" per observation
if len(Obs) < 24: fig.set_size_inches((7, 6))
else: figWidth = fig.set_size_inches((len(Obs) * 0.3, 6))


#Set x axis for subplots to increment sprint number with an extra sprint for forecast
plt.setp((ax1, ax2), xticks=range(1, len(Obs) + 1, 1))

#Set subplots' x & y axis labels; add grid for graph's readability
plt.setp(ax1, xlabel="Sprint Number")
plt.setp(ax1, ylabel="Velocity")
ax1.grid(color="lightgray", alpha=0.5)
plt.setp(ax2, xlabel="Observation (Ascending Order)")
plt.setp(ax2, ylabel="Velocity")
ax2.grid(color="lightgray", alpha=0.5)


###---                 ---###
###--- Sub-Plots Lists ---###
###---                 ---###
    

#Lists for both sub-plots to be completed just-in-time
x, yl, yu = [], [], []  #x and y coordinates for lower/upper CI values (each y coordinate will share an x coordinate)
xm, ym = [], []         #x amd y coordinates for Mean Valid Velocity

x1Gray, x1Cyan, x1Green, x1Magenta, x1Red = [], [], [], [], [] #x coordinates for the velocity observations stored in color-coded lists to support a legend
y1Gray, y1Cyan, y1Green, y1Magenta, y1Red = [], [], [], [], [] #y coordinates for the velocity observations stored in color-coded lists to support a legend

x2Gray, x2Cyan, x2Green, x2Magenta, x2Red = [], [], [], [], [] #x coordinates for the velocity observations stored in color-coded lists to support a legend
y2Gray, y2Cyan, y2Green, y2Magenta, y2Red = [], [], [], [], [] #y coordinates for the velocity observations stored in color-coded lists to support a legend


###---                      ---###
###--- Generate Simple Data ---###
###---                      ---###


'''
#for simplified velocity view
ax1.plot(range(1, len(Obs) + 1), Obs, color="blue", label="Sprint Velocity")

for i, ob in enumerate(Obs):
    ym.append(Mean(Obs[i::-1]))
ax1.plot(range(1, len(Obs) + 1), ym, color="Orange", label="Team Velocity")

ax1.legend(fontsize="x-small", ncol=3)
'''


###---                            ---###
###--- Generate Top Sub-Plot Data ---###
###---                            ---###


#for each velocity observation:
for i, ob in enumerate(Obs):
    #0-based indexing to 1-based counting
    j = i + 1
        
    if len(ValObs(i)) < 2: pass #until there are two valid velocity observations, calculations are irrelevant
    else:
        #Calculate the Mean Valid Velocity, Lower Confidence Interval Value, and Upper Confidence Interval Value (i.e. ym, yl, & yu respectively)
        
        #Calculate the Mean Valid Velocity and store (x, y) coordinates
        ym.append(Mean(ValObs(i)))
        xm.append(j)

        #Calculate the Lower/Upper CI Values and store (x, y) coordinates
        if len(ValObs(i)) < 7:
            #until the 7th valid observation, the CI range is equal to the range of the valid Velocity observations
            yl.append(ValObsSorted(i)[0])
            yu.append(ValObsSorted(i)[-1])
        else:
            #for the 7th+ valid observation, calculate the CI range as detailed @ https://www.mountaingoatsoftware.com/tools/velocity-range-calculator?#
            yl.append(ValObsSorted(i)[LowerCII(len(ValObsSorted(i)))])
            yu.append(ValObsSorted(i)[UpperCII(len(ValObsSorted(i)))])
        x.append(j + 1) #j + 1 due to the CI forecasting the FUTURE sprint's Velocity observation
    
    #plot the observations
    if ob < 0:
        #if the observation is not valid save in red (invalid) lists
        x1Red.append(j)
        y1Red.append(abs(ob))
    else:
        #otherwise the observation is valid
        if len(ValObs(i)) <= 2:
            #if the observation is first or second valid observation, there's no comparision to be made ergo save in gray (unknown) listing
            x1Gray.append(j)
            y1Gray.append(ob)
        else:
            #otherwise a comparison can be made
            if ob < yl[-2]:
                #if the observation is lower than the CI range, save in the cyan (low) listing
                x1Cyan.append(j)
                y1Cyan.append(ob)
            elif ob > yu[-2]:
                #if the observation is higher than the CI range, save in the magenta (high) listing
                x1Magenta.append(j)
                y1Magenta.append(ob)
            else:
                #if the observation is within the CI range, save in the green (nominal) listing
                x1Green.append(j)
                y1Green.append(ob)
  
#velocity observations before CI Forecasting is available
ax1.scatter(x1Gray, y1Gray, color="gray", label="Observed before Forecasting CI")
#velocity observations falling below forecasted CI
ax1.scatter(x1Cyan, y1Cyan, color="cyan", label="Below Forecasted CI")
#velocity observations falling within forecasted CI
ax1.scatter(x1Green, y1Green, color="green", label="Within Forecasted CI")
#velocity observations falling above forecasted CI
ax1.scatter(x1Magenta, y1Magenta, color="magenta", label="Above Forecasted CI")
#velocity observations not valid for CI forecasting
ax1.scatter(x1Red, y1Red, color="red", marker="x", label="Invalid Observation")

#Plot Upper/Lower Confidence Interval values and shade region between the two lines
ax1.plot(x, yu, color="magenta", linestyle="dotted", label="Upper Confidence Interval Value")
ax1.plot(x, yl, color="cyan", linestyle="dotted", label="Lower Confidence Interval Value")
ax1.fill_between(x, yl, yu, color="green", alpha=0.1, label="Forecasted Confidence Interval Range")

#Annotate values of the forecasted 90% Confidence Interval
ax1.annotate("{}".format(yu[-1]), xy=(x[-1] + 0.1, yu[-1] + 0.6), color="magenta", horizontalalignment='left')
ax1.annotate("{}".format(yl[-1]), xy=(x[-1] + 0.1, yl[-1] - 0.6), color="cyan", horizontalalignment='left')

#Shade region within all forecasted Confidence Interval regions
ShadeOverlap(ax1, x)

#Average of Observed Valid Velocities
ax1.plot(xm, ym, color="black", linestyle="dashed", label="Mean Valid Velocity")

#Annotate values of the Mean Valid Velocity
ax1.annotate("{}".format(ym[-1]), xy=(xm[-1] + 0.1, ym[-1] - 0.6), color="black", horizontalalignment='left')

#add legend for sub-plot
ax1.legend(fontsize="x-small", ncol=3)

#invisible dot ensuring annotations will not get cut off from view
ax1.scatter(len(Obs) + 1, sorted([abs(o) for o in Obs])[-1] + 1, color="yellow", alpha=0)



###---                               ---###
###--- Generate Bottom Sub-Plot Data ---###
###---                               ---###


#Order ALL observations in ascending order
ObsSorted = sorted(Obs, key=abs)

for i, ob in enumerate(ObsSorted):
    #0-based indexing to 1-based counting
    j = i + 1 

    if ob < 0:
        #if the observation is not valid save in red (invalid) lists
        x2Red.append(j)
        y2Red.append(abs(ob))
    else:
        #otherwise the observation is valid and a comparison can be made
        if ob < yl[-2]:
            #if the observation is lower than the CI range, save in the cyan (low) listing
            x2Cyan.append(j)
            y2Cyan.append(ob)
        elif ob > yu[-2]:
            #if the observation is higher than the CI range, save in the magenta (high) listing
            x2Magenta.append(j)
            y2Magenta.append(ob)
        else:
            #if the observation is within the CI range, save in the green (nominal) listing
            x2Green.append(j)
            y2Green.append(ob)


#velocity observations falling below forecasted CI
ax2.scatter(x2Cyan, y2Cyan, color="cyan", label="Low Velocity")
#velocity observations falling within forecasted CI
ax2.scatter(x2Green, y2Green, color="green", label="Confident Velocity")
#velocity observations falling above forecasted CI
ax2.scatter(x2Magenta, y2Magenta, color="magenta", label="High Velocity")
#velocity observations not valid for CI forecasting
ax2.scatter(x2Red, y2Red, color="red", marker="x", label="Invalid Observation")

CIX = range(1, len(Obs) + 1 )
UCI = [yu[-1]] * len(CIX)
LCI = [yl[-1]] * len(CIX)

#Plot the Mean Valid Velocity
ax2.plot(CIX, [Mean(ValObs(len(Obs)))] * len(CIX), color="black", linestyle="dashed", label="Mean Valid Velocity")

#Annotate values of the Mean Valid Velocity
ax2.annotate("{}".format(ym[-1]), xy=(CIX[-1] + 0.1, ym[-1] + 0.6), color="black", horizontalalignment='left')

#plot upper and lower CI values through all previously observed velocities
ax2.plot(CIX, UCI, color="magenta", linestyle="dotted", label="Upper Confidence Interval Value")
ax2.plot(CIX, LCI, color="cyan", linestyle="dotted", label="Lower Confidence Interval Value")

#Annotate values of the forecasted 90% Confidence Interval
ax2.annotate("{}".format(yu[-1]), xy=(CIX[-1] + 0.1, yu[-1] + 0.6), color="magenta", horizontalalignment='left')
ax2.annotate("{}".format(yl[-1]), xy=(CIX[-1] + 0.1, yl[-1] - 0.6), color="cyan", horizontalalignment='left')

#shade the areas above/within/below Confidence Interval range magenta/green/cyan
ax2.fill_between(CIX, UCI, [ValObsSorted(len(Obs))[-1]] * len(CIX), color="magenta", alpha=0.1, label="Observations above CI Range")
ax2.fill_between(CIX, UCI, LCI, color="green", alpha=0.1, label="Confidence Interval Range")
ax2.fill_between(CIX, LCI, [ValObsSorted(len(Obs))[0]] * len(CIX), color="cyan", alpha=0.1, label="Observations above CI Range")

#Shade region within all forecasted Confidence Interval regions
ShadeOverlap(ax2, CIX)

#add legend for sub-plot
ax2.legend(fontsize="x-small", ncol=3)

#invisible dot ensuring annotations will not get cut off from view
ax2.scatter(len(Obs) + 1, sorted([abs(o) for o in Obs])[-1] + 1, color="yellow", alpha=0)


###---                  ---###
###--- Render Sub-Plots ---###
###---                  ---###
    

#Render the figure with its subplots
plt.show()