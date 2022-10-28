import time

from modbus_command_module import execute_command ,average_executed_command ,write_to_port_and_get_response
import driver

import serial_module

NUMBER_OF_MAX_RETRIES = 5
WAIT_RESPONSE_SECONDS = 2

DESIRED_DRIVER_FREQUENCY_HZ = 0


Inv_BESS_Current_Ref = None
Dri_DC_voltage = None
Dri_Frequency = None
Dri_Power = None
Inv_Load_Power = None
Inv_BESS_Power = None
Inv_BESS_Voltage = None
Inv_BESS_Current = None



def setup_block():
        global Inv_BESS_Current_Ref
        execute_command("inverter_read_Inv_BESS_Voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

        execute_command("driver_stop", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        time.sleep(10)
        execute_command("driver_enable_PV_mode", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)  
        execute_command("driver_enable_voltage_reference_control_mode", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        execute_command("driver_enable_pv_input", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)    
        execute_command("driver_select_SVPWM_control", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        execute_command("driver_select_communication_running_command_channel", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)    
        execute_command("driver_select_deceleration_to_stop", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)     
        execute_command("driver_select_motor_type_as_asynchronous", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)      
        execute_command("driver_set_rated_power_2_2kW", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)              
        execute_command("driver_set_rated_frequency_50Hz", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)       
        execute_command("driver_set_rated_speed_2870rpm", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)      
        execute_command("driver_set_rated_voltage_220V", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)    
        execute_command("driver_set_rated_current_13_8A", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)   
        execute_command("driver_set_upper_limit_frequency_50Hz", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)    
        execute_command("driver_set_the_maximum_frequency_50Hz", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)       
        execute_command("driver_set_lower_limit_frequency_0Hz", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

        Inv_BESS_Current_Ref = 50
        execute_command("inverter_set_Inv_BESS_Current_Ref", Inv_BESS_Current_Ref, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        
def measurement_block():
        global Dri_DC_voltage
        global Dri_Frequency
        global Dri_Power
        global Inv_PV_Power
        global Inv_Load_Power
        global Inv_BESS_Power
        global Inv_BESS_Voltage
        global Inv_BESS_Current

        NUMBER_OF_DATA_POINTS = 2
        
        Dri_DC_voltage = float(average_executed_command(NUMBER_OF_DATA_POINTS, "driver_read_Dri_DC_voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10
        Dri_Frequency = float(average_executed_command(NUMBER_OF_DATA_POINTS, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100
        Dri_Power = driver.calculate_motor_power_watts_by_frequency(Dri_Frequency)

        Inv_PV_Power = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_PV_Power", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10
        Inv_Load_Power = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_Load_Power", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10
        Inv_BESS_Power = Inv_PV_Power - Inv_Load_Power

        Inv_BESS_Voltage = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_BESS_Voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100
        Inv_BESS_Current = Inv_BESS_Power / Inv_BESS_Voltage

        print( "Dri_DC_voltage: " + str(Dri_DC_voltage) + "V")
        print( "Dri_Frequency: " + str(Dri_Frequency) + "Hz")
        print( "Dri_Power: " + str(Dri_Power) + "W")
        print( "Inv_PV_Power: " + str(Inv_PV_Power) + "W")
        print( "Inv_Load_Power: " + str(Inv_Load_Power) + "W")
        print( "Inv_BESS_Power: " + str(Inv_BESS_Power) + "W")
        print( "Inv_BESS_Voltage: " + str(Inv_BESS_Voltage) + "V")
        print( "Inv_BESS_Current: " + str(Inv_BESS_Current) + "A")


setup_block()
while True:

        #measurement_block()
        
        driver.drive_motor_at_frequency(30)
       
        
        #driver.drive_motor_at_frequency(DESIRED_DRIVER_FREQUENCY_HZ)
        #execute_command("inverter_set_Inv_BESS_Current_Ref", Inv_BESS_Current_Ref, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

        pass





