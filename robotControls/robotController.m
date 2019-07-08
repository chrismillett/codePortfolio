function robotController(serPort)
%robot controller to:
%find centre of the starting room
%leave room without bumping either side of the door
%navigate to the beacon, drive around in a circle, then bump the wall attached to it
%return back to the starting room
%enter room without bumping either side of door
%find centre of the starting room and stop


%use following command to plot trajectory to a chart:
%plot(cell2mat(datahistory(1:2602,2)),cell2mat(datahistory(1:2602,3)));

%** -- FSM Behaviours -- *
%**findCentre
%**exitRoomBehaviour
%**edgeFollowBehaviour
%**beaconHomingBehaviour
%**beaconCircleAndBumpBehaviour
%**returnToRoomBehaviour
%**enterRoomBehaviour
%**finishBehaviour

%global variables
%initialises lidar sensor
LidarRange = LidarSensorCreate(serPort);
%sets range for  right lidar
[rightLidarM,] = min(LidarRange(1:341));
%set range for front lidar to between 241 and 441
[frontLidarM,] = min(LidarRange(241:441));
%set range for left lidar
[leftLidarM,] = min(LidarRange(341:681));

%read rear sonar sensor
rearSonar = ReadSonar(serPort, 4);
        
%set to true when robot is in centre of room
robotInCentre = false;
            


%value for finding the middle of the room, when this reaches 4 the robot is in the middle
frontBackEqual = 0;
%**findCentre
%finds centre by comparing the values returned by the front lidar and rear sonar sensors
%if they are equal, the robot turns on the spot several times to confirm, after which the next behaviour is actioned
%if they are not equal, the robot adjusts its position and keeps checking
    function findCentre(serPort)
        
        %while lidar and sonar aren't equal adjust posiiton
        while frontLidarM ~= rearSonar
            travelDist(serPort, 0.5, 0.05);
            turnAngle (serPort, 0.2, 15);
        end
        
        %if lidar and sonar equal turn on the spot several times to confirm
        if frontLidarM == rearSonar
            turnAngle (serPort, .2, 45);
            frontBackEqual + 1;
        end
        
        %if lidar and sonar equality confirmed 4 times, robot is in the centre and next behaviour is actioned
        if frontBackEqual == 4
            robotInCentre = true;
        end
    end



%**useDoor
%uses a narrow PID controller to guide the robot through the door to the room by following the edge
    function useDoor(serPort)
        %useDoor PID values
        
        %distance to maintain from edge
        setPoint = 0.1;
        
        %gains for adjustment
        proportionalGain = 100;
        integralGain = 0.5;
        derivativeGain = 0.5;
        
        integralState = 0;
        integralMax = 5;
        integralMin = -5;
        
        while(true)
            
            SetDriveWheelsCreate(serPort, 0.5, 0.5);
            pause(.1)

            
            [LidarM,] = min(LidarRange);
            
            if(LidarM < 2)
                
                derivativeState = 0;
                error =  leftLidarM - setPoint;
                
                proportionalTerm = proportionalGain * error;
                
                integralState = integralState + error;
                
                if (integralState > integralMax)
                    integralState = integralMax;
                    
                elseif (integralState < integralMin)
                    integralState = integralMin;
                end
                
                integralTerm = integralGain * integralState;
                derivativeTerm = derivativeGain * (leftLidarM - derivativeState);
                derivativeState = leftLidarM;
                
                angle = proportionalTerm + integralTerm - derivativeTerm;
                turnAngle(serPort, .2, -angle);
            end
        end
    end

        %**edgeFollow
        %follows the outside edge of the starting room to guide the robot to the beacon
            function edgeFollow(serPort)
                
                %distance to maintain from edge
                setPoint = 0.5;
                
                %gains for adjustment
                proportionalGain = 100;
                integralGain = 0.5;
                derivativeGain = 0.5;
                
                integralState = 0;
                integralMax = 5;
                integralMin = -5;
                
                derivativeState = 0;
                
        
                while(true)
                    
                    SetDriveWheelsCreate(serPort, 0.5, 0.5);
                    pause(.1)
                   
                    
                    [LidarM,] = min(LidarRange);
                    
                    if(LidarM < 2)
                        
                        derivativeState = 0;
                        error =  leftLidarM - setPoint;
                        
                        proportionalTerm = proportionalGain * error;
                        
                        integralState = integralState + error;
                        
                        if (integralState > integralMax)
                            integralState = integralMax;
                        elseif (integralState < integralMin)
                            integralState = integralMin;
                        end
                        
                        integralTerm = integralGain * integralState;
                        derivativeTerm = derivativeGain * (leftLidarM - derivativeState);
                        derivativeState = leftLidarM;
                        
                        angle = proportionalTerm + integralTerm - derivativeTerm;
                        turnAngle(serPort, .2, -angle);
                        
                    end
                end
            end
        
        %**beaconHoming
        %when a beacon is viewable by tbe camera the robot heads towards it and the next behaviour takes over
        function beaconHoming(serPort)
            while (any(Camera))
                Camera = CameraSensorCreate(serPort);
                if any(Camera) && abs(Camera) > 0.05
                    turnAngle (serPort, .2, (Camera * 6));
                end
                SetDriveWheelsCreate(serPort, 0.4, 0.4);
                pause (.1);
            end
        end
        
        %**beaconBump
        %bumps into the beacon at a perpendicular angle
        %checks that both left and right lidar values are equal
        %if they are, the heading is directly perpendicular
        function beaconCircleAndBump(serPort)

            [BumpFront] = BumpsWheelDropsSensorsRoomba(serPort);
            
            if leftLidarM == rightLidarM
                SetDriveWheelsCreate(serPort, 0.3, 0.3);
            end
            
            if BumpFront
                if frontLidarM < 2
                    turnAngle (serPort, .2, 90);
                end
            end
        end
        
        
        
        %**finish
        %once the robot is back in the starting room, find the centre again
        %and stop moving, ending the simulation
        function finish(serPort)
            findCentre;
            % Stop motors
            SetDriveWheelsCreate(serPort, 0, 0);
            
        end
            
    while true
        % ****** Finite State Machine Switch *****
        %start robot controller in centre finding behaviour
        behaviour = 'findCentreBehaviour'; 
        if(robotInCentre == true)
            behaviour = exitRoomBehaviour;
        end
        
        switch (behaviour)   
            
            %action behaviour findCentre, making the robot find the centre of the room
            case 'findCentreBehaviour'
                findCentre(serPort);
        
                %the robot exits the starting room, then checks left and right lidar values
                %if one value is greater than 4 and the other is less than or equal to 2, change behaviour to edgeFollow
            case 'exitRoomBehaviour'
                disp('**Behaviour is now exitRoom');
                while ~(leftLidarM > 4 && rightLidarM <= 2) && ~(leftLidarM <= 2 && rightLidarM < 4)
                    useDoor(serPort);
                end
                if leftLidarM > 4 && rightLidarM <= 2
                    behaviour = edgeFollowBehaviour;
                elseif leftLidarM <= 2 && rightLidarM < 4
                    behaviour = 'edgeFollowBehaviour';
                end

                %robot follows outside edge of room until bacon is in range
                %when beacon is in range, head towards it
           case 'edgeFollowBehaviour'
                disp('**Behaviour is now edgeFollow');
                edgeFollow(serPort);
                Camera = CameraSensorCreate(serPort);
                if any(Camera) && abs(Camera) > 0.05
                    behaviour = 'beaconHomingBehaviour';
                end
 
                %follow the beacon until within 0.2m, then change behaviour to circle and bump the beacon
            case 'beaconHomingBehaviour' 
                disp('**Behaviour is now beaconHoming');
                beaconHoming(serPort);
                
                %if either of the three lidar sensors gets a range of less than 0.2m
                %switch to circling the beacon and bumping into the wall
                if (leftLidarM < 0.2 || frontLidarM < 0.2 || rightLidarM < 0.2)
                    behaviour = 'beaconCircleAndBumpBehaviour';
                end
                
                %circle around and then bump the behaviour
            case 'beaconCircleAndBumpBehaviour'
                disp('**Behaviour is now beaconCircleAndBump'); 
                beaconCircleAndBump(serPort);
            
            case 'returnToRoomBehaviour'
                disp('**Behaviour is now returnToRoom');
                edgeFollow(serPort);
                if leftLidarM > 4 && rightLidarM <= 2
                    behaviour = 'edgeFollowBehaviour';
                end
                
                if leftLidarM <= 2 && rightLidarM > 4
                    behaviour = 'edgeFollowBehaviour';
                end
                
            case 'enterRoomBehaviour'
                disp('**Behaviour is now enterRoom');
                useDoor(serPort);
        
            case 'finishBehaviour'
                disp('**Behaviour is now finish');
                findCentre(serPort);
            
            otherwise
                disp('No Behaviour');
        end  
    end
    
            
end

