import time

from modbus_command_module import execute_command ,average_executed_command ,write_to_port_and_get_response
import driver

import serial_module

NUMBER_OF_MAX_RETRIES = 5
WAIT_RESPONSE_SECONDS = 2

Dri_Frequency_Ref = 0


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
        
def measurement_block(start_time_time_seconds, min_duration_seconds):
        global Dri_DC_voltage
        global Dri_Frequency
        global Dri_Power
        global Inv_PV_Power
        global Inv_Load_Power
        global Inv_BESS_Power
        global Inv_BESS_Voltage
        global Inv_BESS_Current

        NUMBER_OF_DATA_POINTS = 1
        
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

        while True:
                if time.time()-start_time_time_seconds > min_duration_seconds:
                        break

PREVIOUS_ALGORITHM_ENTER_TIME = None
def algorithm_block_1():
        global PREVIOUS_ALGORITHM_ENTER_TIME
        global Dri_Frequency_Ref
        global Inv_BESS_Current_Ref
        global Inv_BESS_Power
        global Dri_Frequency
        global Dri_Power
        global Inv_BESS_Voltage
    
        DEFINED_ALGORITHM_PERIOD_SECONDS = 600 
        
        if PREVIOUS_ALGORITHM_ENTER_TIME == None or time.time()-PREVIOUS_ALGORITHM_ENTER_TIME > DEFINED_ALGORITHM_PERIOD_SECONDS:
                PREVIOUS_ALGORITHM_ENTER_TIME = time.time()
                #below code exucutes every 10 minutes
                Algorithm_Check = True
                if Inv_BESS_Power > 100:  
                        if(Dri_Frequency == 0 and (0.7 * Inv_BESS_Power) >1250):
                                if (0.7*Inv_BESS_Power)  <2200:
                                        Inv_BESS_Current_Ref =  (0.3 * Inv_BESS_Power)/Inv_BESS_Voltage
                                else:
                                        Inv_BESS_Current_Ref = (Inv_BESS_Power - 2200)/Inv_BESS_Voltage

                                Dri_Frequency_Ref = 50
                        
                        elif(Dri_Frequency>10 and Dri_Frequency <49.7):
                                if 0.7*(Inv_BESS_Power+ Dri_Power)  <2200:
                                        Inv_BESS_Current_Ref = 0.3* (Inv_BESS_Power + Dri_Power) / Inv_BESS_Voltage

                                else:
                                        Inv_BESS_Current_Ref = (Inv_BESS_Power + Dri_Power - 2200)/Inv_BESS_Voltage
                                
                elif(Inv_BESS_Power> -100 and Inv_BESS_Power < 100):
                        Dri_Frequency_Ref = 50
                
                return True
        
        else:
                return False


def algorithm_block_2():
        global Dri_Frequency
        global Inv_BESS_Current
        global Inv_BESS_Current_Ref

        if(Dri_Frequency > 49.7 or Dri_Frequency == 0):
                if(abs(Inv_BESS_Current - Inv_BESS_Current_Ref) < 1):
                        Inv_BESS_Current_Ref= min( Inv_BESS_Current_Ref +2 , 50)

def algorithm_block_3():
        global Dri_Frequency_Ref
        global Inv_BESS_Power
        global Inv_BESS_Current_Ref

        if Inv_BESS_Power < 100:
                Inv_BESS_Current_Ref = 5
                if Inv_BESS_Power < -100:
                        Dri_Frequency_Ref = 0



def driver_block(frequency):
        if( frequency < 0 or frequency > 50):
                frequency = 0
        driver.drive_motor_at_frequency(frequency)

def BESS_block():
        global Inv_BESS_Current_Ref
        Inv_BESS_Current_Ref = min(Inv_BESS_Current_Ref, 50)
        Inv_BESS_Current_Ref = max(Inv_BESS_Current_Ref, 5)
        execute_command("inverter_set_Inv_BESS_Current_Ref", Inv_BESS_Current_Ref, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, True)

#===================================================================================================

setup_block()
while True: 
        measurement_block(time.time(), 15)       
       

        if ( algorithm_block_1() == True):continue

        algorithm_block_2()
        algorithm_block_3()        

        BESS_block()
        driver_block(Dri_Frequency_Ref)
        
        pass





