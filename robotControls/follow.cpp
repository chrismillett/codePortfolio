#include <iostream>
#include <stdlib.h>
#include <Aria.h>

#include "follow.h"
// Implementation

// Constructor
follow::follow() : ArAction("Follow Edge")
{
  speed = 200; // Set the robots speed to 50 mm/s. 200 is top speed
  deltaHeading = 0; // Straight line

  setPoint = 500; // 0.5 m

  // Proportional control
  pGain = 0.65; // CHANGE THIS
  dGain = 65;
  iGain = 0.001;
}

// Body of action
ArActionDesired * follow::fire(ArActionDesired d)
{
 desiredState.reset(); // reset the desired state (must be done)

 // Get sonar readings
 leftSonar = myRobot->getClosestSonarRange(-20, 100);
 rightSonar = myRobot->getClosestSonarRange(-100, 20);



 //calculate which sonar has the smallest distance, use to calculate error
 closest = min(leftSonar, rightSonar);
 
 if (leftSonar < rightSonar)
	{
		error = closest - setPoint;
	}
 else 
	{
	 error = setPoint - closest;
	}


 // Calculate proportional output
 output = error * pGain;

 // Implement control action
 deltaHeading = output; 
 desiredState.setDeltaHeading(deltaHeading);

 error = setPoint - closest;

 pError = pGain * error;
 
 dError = dGain * (pError - error);

 output = pError + dError;

 desiredState.setDeltaHeading(deltaHeading);

 iError += error;

 if (iError < 50 && error != 0) {
	 iError += error;	  
 }
 else {
	 iError = 0;
 }

 output = iError * iGain;
 pError = error;
 desiredState.setDeltaHeading(deltaHeading);



 system("cls");
 std::cout << "Leftsonar"<< leftSonar << std::endl;
 std::cout << "Rightsonar"<< rightSonar << std::endl;
 std::cout << "error"<< error << std::endl;
 std::cout << "output"<< output << std::endl;

 desiredState.setVel(speed); // set the speed of the robot in the desired state
 desiredState.setDeltaHeading(deltaHeading); // Set the heading change of the robot

 return &desiredState; // give the desired state to the robot for actioning
}


