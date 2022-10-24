import time

from modbus_command_module import execute_command ,average_executed_command ,print_latest_replies
import driver

import serial_module

NUMBER_OF_MAX_RETRIES = 10
WAIT_RESPONSE_SECONDS = 1.5

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
        Inv_BESS_Current_Ref = 50
        execute_command("inverter_set_Inv_BESS_Current_Ref", Inv_BESS_Current_Ref, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        
        execute_command("inverter_read_Inv_BESS_Voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

        execute_command("driver_stop", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
        time.sleep(1)
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
        
        Dri_DC_voltage = float(average_executed_command(NUMBER_OF_DATA_POINTS, "driver_read_Dri_DC_voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))
        Dri_Frequency = float(average_executed_command(NUMBER_OF_DATA_POINTS, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))
        Dri_Power = driver.calculate_motor_power_watts_by_frequency(Dri_Frequency)

        Inv_PV_Power = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_PV_Power", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))
        Inv_Load_Power = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_Load_Power", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))
        Inv_BESS_Power = Inv_PV_Power - Inv_Load_Power

        Inv_BESS_Voltage = float(average_executed_command(NUMBER_OF_DATA_POINTS, "inverter_read_Inv_BESS_Voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))
        Inv_BESS_Current = Inv_BESS_Power / Inv_BESS_Voltage


setup_block()
while True:
        # rslt = serial_module.write_to_port_and_get_response("15,6,32,0,0,5\n",WAIT_RESPONSE_SECONDS)
        # print(rslt)
        # rslt_2 = serial_module.write_to_port_and_get_response("16,04,00,17,00,01\n",WAIT_RESPONSE_SECONDS)
        # print(rslt_2)

        # execute_command("inverter_read_Inv_BESS_Voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)
       
        #measurement_block()
        
        #TODO: main algorithm

        #driver.drive_motor_at_frequency(DESIRED_DRIVER_FREQUENCY_HZ)
        #execute_command("inverter_set_Inv_BESS_Current_Ref", Inv_BESS_Current_Ref, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

        pass





