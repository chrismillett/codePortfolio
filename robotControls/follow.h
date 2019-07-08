//signatures

class FSM : public ArAction // class action inherits from ArAction
{
public:
	FSM(); //constructor
	virtual ~FSM() {} // destructor
	virtual ArActionDesired * fire(ArActionDesired d); // body of the action
	ArActionDesired desiredState; //holds robot state ready for actioning

	int speed; //speed of robot in mm/s
	double deltaHeading; //change in heading in degrees

	enum state {
		WANDER,
		FOLLOW_RIGHT_WALL,
		FOLLOW_LEFT_WALL,
		OBSTACLE_ONCOMING,
		RANDOM_TURN
	};

	//readings of left, right and front sonar sensors
	double leftSonar;
	double rightSonar;
	double frontSonar;

	//FSM state
	state currentState;

	//starting coordinates for wander behaviour
	double startWanderXCoords;
	double startWanderYCoords;
	double wanderDistance;

	//control variables
	double error; // current error
	double output; // final output signal

	ArTime startedRandom;
	int randomWaitDistance;

	//speeds
#define TOP_SPEED 500 // 0.5m/s

	//distance thresholds
#define DISTANCE_FROM_OBSTACLE 100 // robot will avoid obstacles within 0.1m
#define FIND_DISTANCE_TO_WALL 1000 // robot will follow any edges detected within 1.0m 
#define FOLLOW_DISTANCE_TO_WALL 500 // robot will follow wall at a distance of 0.5m
};
