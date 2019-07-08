#include "Aria.h"
#include "follow.h"

//variables for PID
double dState; // input of last position
double iMax, iMin;
double iState; // integrator state

			   // maximum, minimum allowed integtator state
double iGain; // integral gain
double pGain; // proportional gain
double dGain; // derivative gain

			  // generates a random integer between int min and int max inclusive
int rngBetween(int min, int max) {
	return rand() % (max - min + 1) + min;
}

//calculating distance for random turning using pythagoras' theorem
double distanceBetweenPoints(double x1, double y1, double x2, double y2) {
	return sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}


//updates PID values
double updatePID(double error, double position) {
	double pTerm;
	double dTerm;
	double iTerm;
	//calculate proportional term
	pTerm = pGain * error;

	//calculate integratal state with appropriate limits
	iState += error;
	//if error is greater than allowed max iState resets to max
	if (iState > iMax) {
		iState = iMax;
	}
	//if error is less than allowed min iState resets to min
	else if (iState < iMin) {
		iState = iMin;
	}

	iTerm = iGain * iState; //calculate integral term
	dTerm = dGain * (position - dState); //calculate deriative term
	dState = position;

	return pTerm + iTerm - dTerm;
}

//constructor
FSM::FSM() : ArAction("FSM")
{
	currentState = WANDER;
	//set starting wander coordinates to zero
	startWanderXCoords = 0;
	startWanderYCoords = 0;
	wanderDistance = rngBetween(500, 1500);

	speed = TOP_SPEED; // 0.5m/s
	deltaHeading = 0; // change current heading by 0 degrees

	//set PID values
	pGain = 0.40;
	iGain = 85;
	dGain = 65;
}

boolean obstacleLeft = false;

//body of action
ArActionDesired * FSM::fire(ArActionDesired d) {
	//read sonar readings from left, right and front sonar
	leftSonar = myRobot->getClosestSonarRange(-20, 100);
	rightSonar = myRobot->getClosestSonarRange(-100, 20);
	frontSonar = myRobot->getClosestSonarRange(-20, 20);

	/*current distance robot has travelled from moment
	wandering behaviour started this cycle*/
	double currentTravelDistance = distanceBetweenPoints(startWanderXCoords, startWanderYCoords,
		myRobot->getX(), myRobot->getY());

	switch (currentState) {
	case WANDER:
		printf("State is now WANDER \n");
		speed = TOP_SPEED;

		//set robot back to moving straight
		deltaHeading = 0;

		/*checking for obstacles 1100 ahead of the
		front sonar sensor gives the robot enough
		time to slow down before it collides*/
		if (frontSonar < (DISTANCE_FROM_OBSTACLE + 1100)) {
			currentState = OBSTACLE_ONCOMING;
			obstacleLeft + (leftSonar < rightSonar);
		}
		else if (leftSonar < FIND_DISTANCE_TO_WALL) {
			currentState = FOLLOW_LEFT_WALL;
		}
		else if (rightSonar < FIND_DISTANCE_TO_WALL) {
			currentState = FOLLOW_RIGHT_WALL;
		}

		/*if no changes made to current state this
		checks if the robot has wandered too far*/
		if (currentState == WANDER) {
			if (currentTravelDistance > wanderDistance) {
				//turns a random distance between 0.5m and 1.5m
				currentState = RANDOM_TURN;
				startedRandom.setToNow();
			}

		}
		break;

	case OBSTACLE_ONCOMING:
		printf("State is now OBSTACLE_ONCOMING\n");
		speed = 0;
		//turns robot right if there is an obstacle to the left
		deltaHeading = obstacleLeft ? -30 : 30;

		//if an obstacle is no longer close to robot, returns to wander behaviour
		if (frontSonar >= DISTANCE_FROM_OBSTACLE + 1000) {
			currentState = WANDER;
			startWanderXCoords = myRobot->getX();
			startWanderYCoords = myRobot->getY();
		}
		break;

	case RANDOM_TURN:
		printf("State is now RANDOM_TURN \n");
		speed = 0;

		//turn to randomly generated angle between -140 and 140 degrees
		deltaHeading = rngBetween(-140, 140);

		if (rngBetween(0, 1) == 0) {
			deltaHeading = -deltaHeading;
		}

		if (startedRandom.mSecSince() > 2000) {
			currentState = WANDER;
			startWanderXCoords = myRobot->getX();
			startWanderYCoords = myRobot->getY();
			wanderDistance = rngBetween(500, 1500);
		}
		break;

	case FOLLOW_LEFT_WALL:
		printf("State is now FOLLOW_LEFT_WALL\n");
		speed = TOP_SPEED;

		//find error
		if (leftSonar < (2 * FOLLOW_DISTANCE_TO_WALL)) {
			//left distance < 1m
			error = (FOLLOW_DISTANCE_TO_WALL - leftSonar);
			deltaHeading = -updatePID(error, leftSonar);
		}
		else {
			//if no error, return behaviour to wander
			currentState = WANDER;
			startWanderXCoords = myRobot->getX();
			startWanderYCoords = myRobot->getY();
			wanderDistance = rngBetween(500, 1500);
		}

		//check front sonar even when following a wall in case of upcoming obstacles
		if (frontSonar < (DISTANCE_FROM_OBSTACLE + 1000)) {
			currentState = OBSTACLE_ONCOMING;
			speed = 0;
			deltaHeading = 0;
			obstacleLeft = (leftSonar < rightSonar);
		}
		break;
	case FOLLOW_RIGHT_WALL:
		printf("State is now FOLLOW_RIGHT_WALL \n");
		speed = TOP_SPEED;

		//find error
		if (rightSonar < (2 * FOLLOW_DISTANCE_TO_WALL)) {
			//right distance < 1m
			error = -(rightSonar - FOLLOW_DISTANCE_TO_WALL);
			deltaHeading = updatePID(error, rightSonar);
		}
		else {
			//if no error, return behaviour to wander
			currentState = WANDER;
			startWanderXCoords = myRobot->getX();
			startWanderYCoords = myRobot->getY();
			wanderDistance = rngBetween(500, 1500);
		}

		//check front sonar even when following a wall in case of upcoming obstacles
		if (frontSonar < (DISTANCE_FROM_OBSTACLE + 1000)) {
			currentState = OBSTACLE_ONCOMING;
			speed = 0;
			deltaHeading = 0;
			obstacleLeft = (leftSonar < rightSonar);
		}
		break;
	}

	desiredState.reset(); //desired set must be reset
	desiredState.setVel(speed); // set robot's speed while in desired state
	desiredState.setDeltaHeading(deltaHeading); // set new angle for delta heading

	return &desiredState; // give robot desired state to be actioned

}
