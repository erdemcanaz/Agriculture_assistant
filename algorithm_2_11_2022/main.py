import time

from modbus_module import execute_command ,average_executed_command 
import driver_module
from logger_module import append_to_txt_file


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
        append_to_txt_file("algorithm_steps", "EXECUTING SETUP BLOCK", append_datetime_to_data=True)
        
        execute_command("inverter_read_Inv_BESS_Voltage")
        execute_command("driver_stop")
        append_to_txt_file("algorithm_steps", "Stopped the motor, will wait 10 seconds", append_datetime_to_data=True)
        time.sleep(10)
        execute_command("driver_enable_PV_mode")  
        append_to_txt_file("algorithm_steps", "Driver PV mode is enabled", append_datetime_to_data=True)

        execute_command("driver_enable_voltage_reference_control_mode")
        append_to_txt_file("algorithm_steps", "Driver voltage reference control mode is enabled", append_datetime_to_data=True)

        execute_command("driver_enable_pv_input")    
        append_to_txt_file("algorithm_steps", "Driver PV input is enabled", append_datetime_to_data=True)

        execute_command("driver_select_SVPWM_control")
        append_to_txt_file("algorithm_steps", "Driver SVPWM control is selected", append_datetime_to_data=True)
        
        execute_command("driver_select_communication_running_command_channel")    
        append_to_txt_file("algorithm_steps", "Driver communication running command channel is selected", append_datetime_to_data=True)

        execute_command("driver_select_deceleration_to_stop")     
        append_to_txt_file("algorithm_steps", "Driver deceleration to stop is selected", append_datetime_to_data=True)

        execute_command("driver_select_motor_type_as_asynchronous")      
        append_to_txt_file("algorithm_steps", "Driver motor type is set as asynchronous", append_datetime_to_data=True)

        execute_command("driver_set_rated_power_2_2kW")              
        append_to_txt_file("algorithm_steps", "Driver rated power is set as 2.2kW", append_datetime_to_data=True)

        execute_command("driver_set_rated_frequency_50Hz")     
        append_to_txt_file("algorithm_steps", "Driver rated frequency is set to 50Hz", append_datetime_to_data=True)

        execute_command("driver_set_rated_speed_2870rpm") 
        append_to_txt_file("algorithm_steps", "Driver rated speed is set to 2870 rpm", append_datetime_to_data=True)

        execute_command("driver_set_rated_voltage_220V")    
        append_to_txt_file("algorithm_steps", "Driver rated voltage is set to 220V", append_datetime_to_data=True)

        execute_command("driver_set_rated_current_13_8A")   
        append_to_txt_file("algorithm_steps", "Driver rated current is set to 13.8A", append_datetime_to_data=True)

        execute_command("driver_set_upper_limit_frequency_50Hz")    
        append_to_txt_file("algorithm_steps", "Driver upper frequency limit is set to 50Hz", append_datetime_to_data=True)

        execute_command("driver_set_the_maximum_frequency_50Hz")       
        append_to_txt_file("algorithm_steps", "Driver maximum frequency is set to 50Hz", append_datetime_to_data=True)

        execute_command("driver_set_lower_limit_frequency_0Hz")
        append_to_txt_file("algorithm_steps", "Driver lower frequency limit is set to 0Hz", append_datetime_to_data=True)

        Inv_BESS_Current_Ref = 50
        execute_command(command_key = "inverter_set_Inv_BESS_Current_Ref", value = Inv_BESS_Current_Ref)
        append_to_txt_file("algorithm_steps", f"Inverter maximum BESS charging current is set to {Inv_BESS_Current_Ref}A", append_datetime_to_data=True)
        
def measurement_block(start_time_time_seconds, min_duration_seconds):
        append_to_txt_file("algorithm_steps", "EXECUTING MEASUREMENT BLOCK", append_datetime_to_data=True)
        global Dri_DC_voltage
        global Dri_Frequency
        global Dri_Power
        global Inv_PV_Power
        global Inv_Load_Power
        global Inv_BESS_Power
        global Inv_BESS_Voltage
        global Inv_BESS_Current

        global Inv_BESS_Current_Ref
        global Dri_Frequency_Ref
         
        Dri_DC_voltage = float(average_executed_command(command_key =  "driver_read_Dri_DC_voltage", number_of_averaging= 1))/10
        append_to_txt_file("algorithm_steps", f"Driver DC link voltage is measured as {Dri_DC_voltage} V", append_datetime_to_data=True)


        Dri_Frequency = float(average_executed_command(command_key = "driver_read_Dri_Frequency", number_of_averaging= 1))/100
        append_to_txt_file("algorithm_steps", f"Driver frequency is measured as {Dri_Frequency} Hz", append_datetime_to_data=True)

        Dri_Power = driver_module.calculate_motor_power_watts_by_frequency(Dri_Frequency)
        append_to_txt_file("algorithm_steps", f"Using frequency, driver power is calculated as {Dri_Power} Watts", append_datetime_to_data=True)


        Inv_PV_Power = float(average_executed_command(command_key = "inverter_read_Inv_PV_Power",number_of_averaging= 1))/10
        append_to_txt_file("algorithm_steps", f"Inverter PV power is measured as {Inv_PV_Power} Watts", append_datetime_to_data=True)

        Inv_Load_Power = float(average_executed_command(command_key =  "inverter_read_Inv_Load_Power", number_of_averaging= 1))/10
        append_to_txt_file("algorithm_steps", f"Inverter load power is measured as {Inv_PV_Power} Watts", append_datetime_to_data=True)
        
        Inv_BESS_Power = Inv_PV_Power - Inv_Load_Power
        append_to_txt_file("algorithm_steps", f"Inverter bess power (that charges BESS) is  calculated as {Inv_PV_Power} Watts", append_datetime_to_data=True)



        Inv_BESS_Voltage = float(average_executed_command(command_key =  "inverter_read_Inv_BESS_Voltage", number_of_averaging= 1))/100
        append_to_txt_file("algorithm_steps", f"BESS voltage is measured as {Inv_BESS_Voltage} V", append_datetime_to_data=True)

        Inv_BESS_Current = Inv_BESS_Power / Inv_BESS_Voltage
        append_to_txt_file("algorithm_steps", f"BESS current is calculated as {Inv_BESS_Current} A", append_datetime_to_data=True)

        print( "Dri_DC_voltage: " + str(Dri_DC_voltage) + "V")
        print( "Dri_Frequency: " + str(Dri_Frequency) + "Hz")
        print( "Dri_Power: " + str(Dri_Power) + "W")
        print( "Inv_PV_Power: " + str(Inv_PV_Power) + "W")
        print( "Inv_Load_Power: " + str(Inv_Load_Power) + "W")
        print( "Inv_BESS_Power: " + str(Inv_BESS_Power) + "W")
        print( "Inv_BESS_Voltage: " + str(Inv_BESS_Voltage) + "V")
        print( "Inv_BESS_Current: " + str(Inv_BESS_Current) + "A")
        print( "Inv_BESS_Current_Ref: " + str(Inv_BESS_Current_Ref) + "A")
        print( "Driver_Frequency_Ref: " + str(Dri_Frequency_Ref) + "Hz")

        append_to_txt_file("algorithm_steps", f"Will stay in measurement block for {min_duration_seconds - (time.time() - start_time_time_seconds ) } seconds", append_datetime_to_data=True)
        while True:
                if time.time()-start_time_time_seconds > min_duration_seconds:
                        break

PREVIOUS_ALGORITHM_ENTER_TIME = None
def algorithm_block_1():
        append_to_txt_file("algorithm_steps", "EXECUTING BLOCK 1", append_datetime_to_data=True)
        global PREVIOUS_ALGORITHM_ENTER_TIME
        global Dri_Frequency_Ref
        global Inv_BESS_Current_Ref
        global Inv_BESS_Power
        global Dri_Frequency
        global Dri_Power
        global Inv_BESS_Voltage
    
        DEFINED_ALGORITHM_PERIOD_SECONDS = 300

        if PREVIOUS_ALGORITHM_ENTER_TIME == None:
                print("TIME LEFT: 0 seconds")
        else:
                print("TIME LEFT: " + str(DEFINED_ALGORITHM_PERIOD_SECONDS - (time.time() - PREVIOUS_ALGORITHM_ENTER_TIME))+ " seconds")
                append_to_txt_file("algorithm_steps", f"{DEFINED_ALGORITHM_PERIOD_SECONDS - (time.time() - PREVIOUS_ALGORITHM_ENTER_TIME)} seconds until next check", append_datetime_to_data= True)



        if PREVIOUS_ALGORITHM_ENTER_TIME == None or time.time()-PREVIOUS_ALGORITHM_ENTER_TIME > DEFINED_ALGORITHM_PERIOD_SECONDS:
                append_to_txt_file("algorithm_steps", f"Checking +/+/+/+/+/+", append_datetime_to_data= True)
                append_to_txt_file("algorithm_steps", f"Before algorithm -> Dri_Frequency_Ref:{Dri_Frequency_Ref}, Inv_BESS_Current_Ref:{Inv_BESS_Current_Ref}, Inv_BESS_Power:{Inv_BESS_Power}, Dri_Frequency:{Dri_Frequency}, Dri_Power:{Dri_Power}, Inv_BESS_Voltage:{Inv_BESS_Voltage}", append_datetime_to_data= True)
                PREVIOUS_ALGORITHM_ENTER_TIME = time.time()
                #below code exucutes every 10 minutes
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
     
                append_to_txt_file("algorithm_steps", f"After algorithm -> Dri_Frequency_Ref:{Dri_Frequency_Ref}, Inv_BESS_Current_Ref:{Inv_BESS_Current_Ref}, Inv_BESS_Power:{Inv_BESS_Power}, Dri_Frequency:{Dri_Frequency}, Dri_Power:{Dri_Power}, Inv_BESS_Voltage:{Inv_BESS_Voltage}", append_datetime_to_data= True)
                return True
        
        else:
                append_to_txt_file("algorithm_steps", f"After algorithm -> Dri_Frequency_Ref:{Dri_Frequency_Ref}, Inv_BESS_Current_Ref:{Inv_BESS_Current_Ref}, Inv_BESS_Power:{Inv_BESS_Power}, Dri_Frequency:{Dri_Frequency}, Dri_Power:{Dri_Power}, Inv_BESS_Voltage:{Inv_BESS_Voltage}", append_datetime_to_data= True)
                return False


def algorithm_block_2():
        append_to_txt_file("algorithm_steps", "EXECUTING BLOCK 2", append_datetime_to_data=True)
        global Dri_Frequency
        global Inv_BESS_Current
        global Inv_BESS_Current_Ref

        append_to_txt_file("algorithm_steps", f"Before algorithm -> Dri_Frequency: {Dri_Frequency}, Inv_BESS_Current_Ref:{Inv_BESS_Current_Ref}, Inv_BESS_Current:{Inv_BESS_Current}", append_datetime_to_data= True)
        if(Dri_Frequency > 49.7):
                if(abs(Inv_BESS_Current - Inv_BESS_Current_Ref) < 2):
                        Inv_BESS_Current_Ref= min( Inv_BESS_Current_Ref +2 , 50)
        append_to_txt_file("algorithm_steps", f"After algorithm -> Dri_Frequency: {Dri_Frequency}, Inv_BESS_Current_Ref:{Inv_BESS_Current_Ref}, Inv_BESS_Current:{Inv_BESS_Current}", append_datetime_to_data= True)



def algorithm_block_3():
        append_to_txt_file("algorithm_steps", "EXECUTING BLOCK 3", append_datetime_to_data=True)
        global Dri_Frequency
        global Dri_Frequency_Ref
        global Inv_BESS_Current
        global Inv_BESS_Current_Ref

        append_to_txt_file("algorithm_steps", f"Before algorithm -> Inv_BESS_Current_Ref: {Inv_BESS_Current_Ref} , Inv_BESS_Current: {Inv_BESS_Current} Dri_Frequency: {Dri_Frequency} Dri_Frequency_Ref:{Dri_Frequency_Ref}", append_datetime_to_data= True)
        if(Dri_Frequency == 0):
                Dri_Frequency_Ref = 0
                if(abs(Inv_BESS_Current - Inv_BESS_Current_Ref) < 2):
                        Inv_BESS_Current_Ref= min( Inv_BESS_Current_Ref +2 , 50)
        append_to_txt_file("algorithm_steps", f"After algorithm -> Inv_BESS_Current_Ref: {Inv_BESS_Current_Ref} , Inv_BESS_Current: {Inv_BESS_Current} Dri_Frequency: {Dri_Frequency} Dri_Frequency_Ref:{Dri_Frequency_Ref}", append_datetime_to_data= True)
                


def algorithm_block_4():
        append_to_txt_file("algorithm_steps", "EXECUTING BLOCK 4", append_datetime_to_data=True)
        global Dri_Frequency_Ref
        global Inv_BESS_Power
        global Inv_BESS_Current_Ref

        append_to_txt_file("algorithm_steps", f"Before algorithm -> Inv_BESS_Power: {Inv_BESS_Power}, Inv_BESS_Current_Ref: {Inv_BESS_Current_Ref} A, Dri_Frequency_Ref: {Dri_Frequency_Ref}", append_datetime_to_data=True)
        if Inv_BESS_Power < 100:
                Inv_BESS_Current_Ref = 5
                if Inv_BESS_Power < -100:
                        Dri_Frequency_Ref = 0

        append_to_txt_file("algorithm_steps", f"After algorithm -> Inv_BESS_Power: {Inv_BESS_Power}, Inv_BESS_Current_Ref: {Inv_BESS_Current_Ref} A, Dri_Frequency_Ref: {Dri_Frequency_Ref}", append_datetime_to_data=True)


def driver_block(frequency):
        append_to_txt_file("algorithm_steps", "EXECUTING DRIVER BLOCK", append_datetime_to_data=True)
        if( frequency < 0 or frequency > 50):
                frequency = 0
        driver_module.drive_motor_at_frequency(frequency)
        append_to_txt_file("algorithm_steps", f"Driver tries to reach {frequency} Hz", append_datetime_to_data=True)

def BESS_block():
        append_to_txt_file("algorithm_steps", "EXECUTING BESS BLOCK", append_datetime_to_data=True)
        global Inv_BESS_Current_Ref
        Inv_BESS_Current_Ref = min(Inv_BESS_Current_Ref, 50)
        Inv_BESS_Current_Ref = max(Inv_BESS_Current_Ref, 5)
        execute_command(command_key = "inverter_set_Inv_BESS_Current_Ref", value = Inv_BESS_Current_Ref)
        append_to_txt_file("algorithm_steps", f"BESS max charging current is set to {Inv_BESS_Current_Ref}", append_datetime_to_data=True)


#===================================================================================================
setup_block()

while True: 
        measurement_block(time.time(), 15)       
       

        rslt = algorithm_block_1()
        algorithm_block_2()

        if rslt == False:
                algorithm_block_3()      
        algorithm_block_4()      

        BESS_block()
        driver_block(Dri_Frequency_Ref)
        
        pass




