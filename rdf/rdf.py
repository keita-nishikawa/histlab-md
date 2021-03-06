# coding: utf-8
import glob
import math
import csv
import numpy as np
import pandas as pd
import itertools
import sys

"""
重心のxvgファイルからxy座標のみ取得
各時間のxy座標を配列にして返す
"""
def fetchLine():
    allFiles = glob.glob('*.xvg')
    counter = 0
    for file in allFiles:
        data = np.loadtxt(file)
        if counter == 0:
            datas = np.delete(data, [0, 3], 1)
        else:
            xydata = np.delete(data, [0, 3], 1)
            datas = np.append(datas, xydata, axis=1)
        counter += 1
        print 'file number :', counter

    rdatas = datas.reshape(datas.shape[0], datas.shape[1]/2, 2)
    return rdatas[range(1, tmax, dt),:]

"""
各時間における粒子間距離を計算
"""
def getDistance(xydatas, particlesNum):
    d = []
    i = 0
    for xy in xydatas:
        for i,j in list(itertools.product(range(particlesNum), repeat=2)):
            x1 = xy[i][0]
            if (x1 > xsize):
                x1 = x1 - xsize
            x2 = xy[j][0]
            if (x2 > xsize):
                x2 = x2 - xsize
            y1 = xy[i][1]
            if (y1 > ysize):
                y1 = y1 - ysize
            y2 = xy[j][1]
            if (y2 > ysize):
                y2 = y2 - ysize
            dx = np.absolute(x1-x2)
            dy = np.absolute(y1-y2)
            #周期境界条件除去
            if float(dx)/xsize > 0.5:
                dx = xsize - dx
            if float(dy)/ysize > 0.5:
                dy = ysize - dy
            #距離計算
            d.append(math.sqrt(dx**2 + dy**2))
    return np.array(d).reshape(times, particlesNum**2)

"""
rdf計算
"""
def calcGr(distanses, particlesNum, times):
    allDensity = particlesNum / (math.pi * diag**2)

    r = 0
    rd = []
    gr = []
    while r < diag:
        c = np.where((r < distanses) & (distanses <= (r + dr)))
        n = len(c[0]) / (particlesNum * times)
        if r == 0:
            drDensity = n / (math.pi * dr**2)
        else:
            drDensity = n / (math.pi * 2 * r * dr)

        gr.append(drDensity / allDensity)
        rd.append(r)
        r += dr

    return pd.Series(rd, gr)

#main
argv = sys.argv
if len(argv) == 4:
    xsize = 30.3483
    ysize = 30.3483
    diag  = 21.5
    dr    = float(argv[1])
    dt    = int(argv[2])
    tmax  = int(argv[3])
else:
    sys.exit()

print 'start file import'
xydatas = fetchLine()
print 'end file import'
particlesNum = xydatas.shape[1]
times = xydatas.shape[0]
print 'start calcurate distanse'
distanses = getDistance(xydatas, particlesNum)
print 'end calcurate distanse'
print 'start calcurate rdf'
gr = calcGr(distanses, particlesNum, times)
print 'end calcurate rdf'
gr.to_csv("rdf.csv")
