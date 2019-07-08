import urllib.request
import json
import time
import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation

url = 'http://127.0.0.1:18080'
sonarAngles = [90, 50, 30, 10, -10, -30, -50, -90, -90, -130, -150, -170, 170, 150, 130, 90]

pathX = []
pathY = []
scatterX = []
scatterY = []


fig = plt.figure()
subplot = fig.add_subplot(1,1,1)

def animatePlot(i, scatterX, scatterY):
    data = json.loads(urllib.request.urlopen(url).read())

    print(data)

    for sonarID in range(0, 15):
        sonarData = data['SonarData'][sonarID]
        sonarAngle = math.radians(sonarAngles[sonarID])

        rx = data['relativePosition']['x']
        ry = data['relativePosition']['y']
        rth = math.radians(data['relativePosition']['th'])

        pathX.append(rx)
        pathY.append(ry)

        if sonarData < 5000:
            abosluteAgnle = rth + sonarAngle

            stX= (math.cos(absoluteAngle) * sonarData) + rx
            stY = (math.sin(absoluteangle) * sonarData) + ry
            
            scatterX.append(stX)
            scatterY.append(stY)

            subplot.clear()
            subplot.scatter(scatterX, scatterY, s=1, c='r')
            subplot.plot(pathX, pathY)


ani = animation.FuncAnimation(fig, animatePlot, fargs=(scatterX, scatterY), interval=100)
plt.show()