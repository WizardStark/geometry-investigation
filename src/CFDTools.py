import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 14})
import pandas as pd
import os

def appender(nparr,desiredLen):
    if len(nparr)<desiredLen:
        delta = desiredLen-len(nparr)
        nparr = np.append(nparr,[nparr[-1]]*delta,axis=0)
    
    return nparr

def normalize(arrToNormalize,axisToNormalize):
    maxVal = max(abs(arrToNormalize[:,axisToNormalize]))
    arrNormalized = np.copy(arrToNormalize)
    arrNormalized[:,axisToNormalize] = arrToNormalize[:,axisToNormalize]/maxVal
    return arrNormalized

def importer(directory:str,nlines:int,axialV:int):
    maxlen = len(np.genfromtxt(directory+'\\vx-line1',skip_header=4,skip_footer=1))
    for i in range(nlines):
        xlen = len(np.genfromtxt(directory+f'\\vx-line{i+1}',skip_header=4,skip_footer=1))
        ylen = len(np.genfromtxt(directory+f'\\vy-line{i+1}',skip_header=4,skip_footer=1))
        zlen = len(np.genfromtxt(directory+f'\\vz-line{i+1}',skip_header=4,skip_footer=1))
        maxlen = max(maxlen,xlen,zlen,ylen)

    arrlen = maxlen

    vx=np.empty([nlines,arrlen,2])
    vy=np.empty([nlines,arrlen,2])
    vz=np.empty([nlines,arrlen,2])

    for i in range(nlines):
        xdata = np.genfromtxt(directory+f'\\vx-line{i+1}',skip_header=4,skip_footer=1)
        ydata = np.genfromtxt(directory+f'\\vy-line{i+1}',skip_header=4,skip_footer=1)
        zdata = np.genfromtxt(directory+f'\\vz-line{i+1}',skip_header=4,skip_footer=1)

        xdata = normalize(xdata,0)
        ydata = normalize(ydata,0)
        zdata = normalize(zdata,0)

        xdata,ydata,zdata = lineReverse(xdata,ydata,zdata)

        xdata = appender(xdata,arrlen)
        ydata = appender(ydata,arrlen)
        zdata = appender(zdata,arrlen)

        xdata[:,1] = xdata[:,1]/axialV
        ydata[:,1] = ydata[:,1]/axialV
        zdata[:,1] = zdata[:,1]/axialV

        vx[i]= xdata
        vy[i]= ydata
        vz[i]= zdata
    return np.array([vx,vy,vz])
# format: section[dimension][line number][points][position/magnitude]

def plotCompare(arrs2compare,arrTitles:str,plottitle:str,dimension:str):
    dimIdx = {'x':0,'y':1,'z':2,'r':0,'t':1}[dimension]
    nlines = len(arrs2compare[0][dimIdx])
    numArrs = len(arrs2compare)
    dim = [int(np.ceil(nlines/2)),2]

    fig, axs = plt.subplots(dim[0], dim[1], sharex = True, sharey=True, figsize = (15,9))
    fig.suptitle(plottitle)
    fig.subplots_adjust(hspace=0.5,wspace=0.3)
    for i in range(nlines):
        for k in range(numArrs):
            temp = arrs2compare[k][dimIdx]
            axs[(x:=(i//dim[1])),(y:=(i%dim[1]))].plot(temp[i,:,0],temp[i,:,1],label = arrTitles[k])
            axs[x,y].set_title(f'Line {i+1}')
            # axs[x,y].legend(loc = 'best')
        if i==nlines-1:
            axs[((i+1)//dim[1]),((i+1)%dim[1])].set_visible(False)
            break

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    plt.xlabel("Normalized distance from centre [$r/r_{max}$]", fontsize = 16)
    plt.ylabel("Normalised velocity [$v_{i}/v_{a,initial}$]", fontsize = 16,labelpad=20)
    
    lines_labels = [fig.axes[0].get_legend_handles_labels()]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    fig.legend(lines, labels, loc = 'lower right',bbox_to_anchor = (0.95,0.15))

    fig.tight_layout()
    fig.subplots_adjust(top=0.92)
                                        
    fig.savefig(f'Figures\{plottitle}.pdf',bbox_inches = 'tight')

def plotDims(arrs2compare,arrTitles:str,plottitles:list,dimensions:str):
    for idx,i in enumerate(dimensions):
        plotCompare(arrs2compare,arrTitles,plottitles[idx],i)

def lineAngle(lineCoords):
    angleFromX=[]
    for i in range(5):
        theta = np.arctan2((lineCoords[i,1,2]-lineCoords[i,0,2]),(lineCoords[i,1,0]-lineCoords[i,0,0]))
        
        angleFromX.append(theta)
    return angleFromX

def cartesianToRadial(vx,vz,lAngle):
    arrshape = vz.shape
    vrad = np.empty(arrshape)
    vtan = np.empty(arrshape)
    for i in range(arrshape[0]):
        for j in range(arrshape[1]):
            x = vx[i,j]
            z = vz[i,j]
            alpha = np.nan_to_num(np.arctan2(z[1],x[1]))
            mag = np.sqrt(z[1]**2+x[1]**2)
            vrad[i,j,0] = x[0]
            vtan[i,j,0] = z[0]
            vrad[i,j,1] = mag*np.cos(alpha-lAngle[i])
            vtan[i,j,1] = mag*np.sin(alpha-lAngle[i])
    return [vrad,vtan]

def lineReverse(arrx,arry,arrz):
    firstHalf = np.sum(arry[(arry[:,0]<=0.5)])/np.sum((arry[:,0]<=0.5))
    secondHalf = np.sum(arry[arry[:,0]>0.5])/np.sum(arry[:,0]>0.5)
    
    if abs(abs(secondHalf)>abs(firstHalf)):
        arrx[:,0] = abs(arrx[:,0]-max(arrx[:,0]))
        arry[:,0] = abs(arry[:,0]-max(arry[:,0]))
        arrz[:,0] = abs(arrz[:,0]-max(arrz[:,0]))

    return arrx,arry,arrz

def summariser(listofpolarArrs,listofCartArrs):
    means = []
    maxes = []
    mins = []
    for i in range(len(listofpolarArrs)):
        arr =  listofpolarArrs[i][1][:,:,1]*100/np.max(listofCartArrs[i][1][:,:,1])
        means.append(np.mean(arr))
        maxes.append(np.max(abs(arr)))
        mins.append(np.min(abs(arr)))

    return [means,maxes,mins]