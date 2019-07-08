from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np
import urllib.request
import json
import math
import random
import time


# Webserver address and port, use 127.0.0.1 instead of localhost, it will be resolved quicker
url = 'http://127.0.0.1:18080'

sonarIDtoAngle = [90, 50, 30, 10, -10, -30, -50, -90, -90, -130, -150, -170, 170, 150, 130, 90]

#Store data here
robotXTraj = []
robotYTraj = []

partAng = []
partList = []
scatterX = []
scatterY = []

actualChangeX = 0
actualChangeY = 0
actualChangeHeading = 0

robotPrevPosX = 0
robotPrevPosY = 0
robotPrevAngle = 0

trajLists = []

firstLoop = True

particleCount = 2500

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

MAP NAME HERE
- this MUST be equal to the map you are using

"""




mapName = 'square'

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importing the map and extracting the lines
filepath = './maps/'+mapName+'.map'
lines = []

with open(filepath) as fp:

   recordinglines = False
   line = fp.readline()
   cnt = 1

   while line:

       print("Reading Line {}: {}".format(cnt, line.strip()))
       line = fp.readline()
       cnt += 1

       if recordinglines:
           if line.strip() != "DATA":
                lines.append(line.strip())

       if line.strip() == "LINES":
           recordinglines = True

lines.remove('')
print("Number of Lines: {}".format(len(lines)))


formattedLines = []

for line in lines:
    linedata = line.split()
    formattedLines.append({'p1': [int(linedata[0]), int(linedata[1])], 'p2':[int(linedata[2]), int(linedata[3])]})




# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Calculate minimum and maximum points from line segments
# Get map file from folder and transpose map (flip upside down)


minX = 0
minY = 0
maxX = 0
maxY = 0

for line in formattedLines:
    p1x = line['p1'][0]
    p1y = line['p1'][1]
    p2x = line['p2'][0]
    p2y = line['p2'][1]

    if p1x < minX:
        minX = p1x
    if p1y < minY:
        minY = p1y

    if p2x < minX:
        minX = p2x
    if p2y < minY:
        minY = p2y

    if p1x > maxX:
        maxX = p1x
    if p1y > maxY:
        maxY = p1y

    if p2x > maxX:
        maxX = p2x
    if p2y > maxY:
        maxY = p2y

print("minX {} minY {} maxX {} maxY {}".format(minX, minY, maxX, maxY))

lengthX = maxX - minX
lengthY = maxY - minY

mapImage = Image.open('./occupancyMaps/'+mapName+'.png')
mapImage_t = mapImage.transpose(Image.FLIP_TOP_BOTTOM)

maxsize = (mapImage_t.width * 100, mapImage_t.height  * 100)
mapTransposedImage = mapImage_t.resize(maxsize)




## =======================================================================================================================

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

def getOccupancyGridValue(x, y):

    xT = x + abs(minX)
    yT = y + abs(minY)

    gridValue = mapTransposedImage.getpixel((xT, yT))[0]

    normalizedValue = (gridValue - 0) / (255 - 0)

    return normalizedValue


print(getOccupancyGridValue(-9020,-2020))
print(getOccupancyGridValue(-8500,-1800))
print(getOccupancyGridValue(1000,1000))

"""

Initial Setup Below Here

- Create and setup particles here, remember to set up the weightings of these particles
- Think of a good data structure to represent the particles

"""

#class for the particles for the particle filter
#essentially plots a potential location for the robot based on the values gathered from the simulator
#these are updated in real time as the robot progresses and the collected values change
class Particle:
    def __init__(self, xPos, yPos, angle):
        self.xPos = xPos
        self.xTraj = []
        self.yPos = yPos
        self.yTraj = []
        self.angle = angle

    def UpdateParticlePos(self, changeInDistance, actualChangeHeading):
        self.xPos = self.xPos + changeInDistance * math.cos(math.radians(self.angle))
        self.xTraj.append(self.xPos)
        self.yPos = self.yPos + changeInDistance * math.sin(math.radians(self.angle)) 
        self.yTraj.append(self.yPos)
        self.angle = self.angle + actualChangeHeading   

    #checks particle's X and Y coordinates to ensure they are within the boundaries of the map
    #if they exceed either -10,000 or 10,000 on the X or Y axis, they are dropped from the array
    def CheckParticle(self):
        if (self.xPos < -10000):
            return False
        if (self.yPos < -10000):
            return False
        if (self.xPos > 10000):
            return False        
        if (self.yPos > 10000):
            return False    
        else:
            return True

        

#adds the created particles to the list ready for the filtering
for x in range(particleCount):
    partList.append(Particle(random.randint(-9999,9999),random.randint(-9999,9999),random.randint(1,360)))


print("***** Beginning Partcle Filter *****")

#res = urllib.request.urlopen(url).read()
time.sleep(1)

def animate(i, scatterX, scatterY):
    """
    Program Loop

    - The time interval of this is 1 sec (1000ms) found in the FuncAnimation call below the function
    - This is called every iteration (once a second)

    Remember you need 3 things:
    	- Belief Probability Density Function (the particles you have)
    	- System Dynamics (you will need to find how the robot moved using Position, then update the particles with this movement plus noise!)
    	- Perceptual Model (we have the occupancy map)

    So...
    	Particles are propogated according to the motion model
    	They are weighted according to the likelihood of the observation
    	They are then resampled to create a new set of particles for the next iteration

    To get the probabilistic value from the occupancy map, use:

    	getOccupancyGridValue(xPos, yPos)

    """
    # request the needed data from the web server and put it to an array for use in the function
    #this same line appears previously in the file, but is needed both in and out of the animate function
    #without it in the function, it doesn't receive any data whatsoever
    #without it out of the function, the particles only contain half of the robot's trajectory
    res = urllib.request.urlopen(url).read()
    data = json.loads(res)
 
    # Get robots current position in the X and Y coordinates
    #then appends this data to the corresponding array for that axis' array
    robotXPos = data['absolutePosition']['x']
    robotXTraj.append(robotXPos)

    robotYPos = data['absolutePosition']['y']
    robotYTraj.append(robotYPos)

    robotAngle = data['absolutePosition']['th']

    """
    1. Update the particles using system dynamics (the prediction phase algorithm in the slides)
    2. Measure the environment for the particle using the sonar sensors (uses the occupancy map) and use this to update the weights
    3. Normalise weights for the particles
    """

    global robotPrevPosX 
    actualChangeX = robotXPos - robotPrevPosX

    global robotPrevPosY
    actualChangeY = robotYPos - robotPrevPosY

    global robotPrevAngle
    actualChangeHeading = robotAngle - robotPrevAngle

    global particleCount

    #works out distance change based on the actual changes in the X and Y coordinates
    changeInDistance = (math.sqrt(actualChangeX*actualChangeX + actualChangeY*actualChangeY))
    #print(changeInDistance)

    global firstLoop

    #this loop updates the particles on the plotted graph
    #it checks if a particle is valid compared to the actual trajectory and deletes those which aren't correct
    if (firstLoop == False):
        x = 0
        while (x < particleCount):
            #
            partList[x].UpdateParticlePos(changeInDistance, actualChangeHeading)
            if (partList[x].CheckParticle() == False):
                print("Particle removed")
                partList.pop(x)
                x -= 1
                particleCount -= 1
            print(x)
            #prints the robot's X and Y coordinates and current heading every cycle
            print("Robot's current X Position: ", robotXPos)
            print("Robot's current Y Position: ", robotYPos)
            print("Robot's current heading: ", robotAngle)
            x = x + 1

    firstLoop = False

    #declares the previous XY coordinates of the robot and its previous heading 
    robotPrevPosX = robotXPos
    robotPrevPosY = robotYPos
    robotPrevAngle = robotAngle



    # Plotting
    # clear plot, add data to new figure
    ax.clear()

    #draws a box to denote the boundaries of the map
    #the particles and actual trajectory will be inside this
    for line in formattedLines:
        ax.plot([line['p1'][0], line['p2'][0]], [line['p1'][1], line['p2'][1]], c='k')

    """
    Draw particles here
    """
    for j in range(particleCount):
        #set the colour of the particle trajectories to yellow
        #the colour of the actual trajectory is blue
        #i chose these just to make the difference between the trajectories more clear
        ax.plot(partList[j].xTraj, partList[j].yTraj, c = 'y')

    ax.plot(robotXTraj, robotYTraj, c='b')

    print("Particle Filter Loop Complete")


#animate the graph with the robot's actual trajectory and the particles
ani = animation.FuncAnimation(fig, animate, fargs=(scatterX, scatterY), interval=100)
# open the plot in a new window
plt.show()



