# Euro Truck Simulator 2

## Game mechanics

 - Drive to target location
	 - Accelerate
	 - Shift gears
	 - Steer
	 - Brake
	 - Interact with traffic
		 - Speed cameras
		 - Slow down for traffic
		 - Right of way
 - Stop at target location
 - Park vehicle
 - Maintenance
	 - Sleep when tired
		 - Detect tiredness
		 - Drive to parking area
		 - Stop at parking area
		 - Press sleep
	 - Fuel up when on empty tank
		 - Detect empty fuel
		 - Drive to fuel location
		 - Stop at fuel location
		 - Press fuel up
 - Select new delivery on delivery completion
	 - Detect
	 - Select

## Models
- RL model
	- Handle driving
		- Rewards	
			- Getting closer towards destination
			- Speed gives reward
        - Punishment 
            - fine's
    - Parking
        - Spam release package
- Algorithms
    - Select new job when complete
	- Toe when broken
	- Turn on lights

## Action spaces
### Driving to target location agent
- Throttle/Break application: Accelerate: 0, Idle: 1, Brake: 2
- Gear control: Shift down: 0, Don't shift: 1, Shift Up: 2
- Steering application: Steer left: 0, Steer straight: 1, Steer right: 2
- Indicators: indicate left: 0, don't indicate: 1, indicate right: 2
