
### USER CONFIGURATION ###

# Actuator Module ###############################################################################
#                                                                                               #
#   Necessary keys:                                                                             #
#   'pin':          The pin of the actuator. A dict is to be used for a stepper motor           #
#                       Example solenoid: board.P0 # Pin 0                                      #
#                       Example servo: board.P1 # Pin 1                                         #
#                       Example stepper motor: {'dir': board.P0, 'step': board.P1}              #
#                                                                                               #
#   Optional keys:                                                                              #
#   'sensor':       The pin designator for the sensor that triggers the actuator, default = 0   #
#   'trigger':      The interger value to trigger the analogue sensor, default = 40000          #
#   'idle_state':   The state of the pin while not active, default = 0                          #
#   'active_state': The state of the pin while active, default = 1                              #
#                       Example solenoid: 1 # HIGH                                              #
#                       Example servo: 60 # Degrees                                             #
#                       Example stepper motor: 1610 # Number of steps from idle_state           #
#																								#
#   'speed':        The speed at which the actuator moves, default = 0                          #
#                       Solenoid: # Disabled           			                                #
#                       Example servo: 200 # Time to reach angle in milliseconds                #
#                       Example stepper motor: 500 # Time between steps in microseconds         #
#						* 'speed' is required for servos and stepper motors						#
#																								#
#   'time':         The time that the actuator is active in milliseconds, default = 0           #
#                       Example solenoid: 2000 # 2 Seconds                                      #
#                       Example servo: 2000 # 2 Seconds                							#
#                       Stepper motor: # Disabled		                                		#
#																								#
#   'delay':        The time to delay next step after being active in milliseconds, default = 0 #
#                       Example solenoid: 2000 # 2 Seconds                                      #
#                       Example servo: 5000 # 5 Seconds                                         #
#                       Example stepper motor: 10000 # 10 Seconds                               #
#																								#
#################################################################################################

actuators = {
				'feed_actuator': 		{'pin': 'LED_RED', 'active_state': 1, 'time': 500, 'delay': 500},
				'gantry_actuator': 		{'pin': {'dir': 'Y5', 'step': 'Y6'}, 'active_state': 1610, 'speed': 500},
				'pre_purge_actuator':	{'pin': 'LED_YELLOW', 'time': 500},
				'post_purge_actuator':	{'pin': 'LED_BLUE', 'time': 500},

				'fill_actuators' : [
                    {'pin': 'LED_RED', 'sensor': 'Y12', 'active_state': 60},
                    {'pin': 'LED_BLUE', 'sensor': 'Y11', 'active_state': 60},
                    {'pin': 'A1', 'sensor': 'A0', 'active_state': 60, 'speed': 50}
                ]
}


start_button_pin    	= "X17"
end_stop_0_pin			= "X17"
end_stop_1_pin			= "X17"

rot_enc_a_pin       	= 0
rot_enc_b_pin       	= 0
rot_enc_button_pin  	= 0

lcd_spi_channel			= 1
lcd_slave_select_pin	= "X5"

sdcard_spi_channel		= 2
sdcard_slave_select_pin	= "Y5"
sdcard_path				= "/sd2"

sensor_frequency_hz		= 100