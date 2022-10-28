import time
from modbus_command_module import execute_command, average_executed_command



def calculate_motor_power_watts_by_frequency(frequency):
    return (27.84392-4.6395*frequency+0.915*pow(frequency,2))

def drive_motor_at_frequency(desired_frequency): 
    WAIT_RESPONSE_SECONDS = 1.125
    NUMBER_OF_MAX_RETRIES = 5
    should_raise_error = True

    freq_initial = None
    if desired_frequency <= 0:
        execute_command("driver_stop", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
        return None
    else:
        execute_command("driver_run", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
        freq_initial = float(average_executed_command(1, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100
        if(freq_initial >=49.7 and desired_frequency >= 49.7):
            print("The frequency is already at the maximum. So I will not change it")
            return None

    #abs_delta_voltage = 6 if freq_initial < 9.5 else 4 
    abs_delta_voltage = 4

    abs_freq_dif_old = abs(desired_frequency-freq_initial)
    avg_dc_link_voltage = float(average_executed_command(2, "driver_read_Dri_DC_voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10

    if desired_frequency > freq_initial:
        aimed_dc_link_voltage = avg_dc_link_voltage - abs_delta_voltage
        execute_command("driver_set_ref_voltage", int(aimed_dc_link_voltage*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
        time.sleep(7.5)

        freq_new = float(average_executed_command(1, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100
        abs_freq_dif_new = abs(desired_frequency-freq_new)

        avg_dc_link_voltage = float(average_executed_command(1, "driver_read_Dri_DC_voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10
        if(abs(avg_dc_link_voltage-aimed_dc_link_voltage) > 12):
            print(f"Impulsive voltage change of {abs(avg_dc_link_voltage-aimed_dc_link_voltage)}V is detected. So I set voltage referecene as same with the dc line voltage : {avg_dc_link_voltage}V")
            execute_command("driver_set_ref_voltage", int(avg_dc_link_voltage*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
            return None

        if(abs_freq_dif_new<abs_freq_dif_old):
            print(f"Right- desired frequency was higher than the frequency now. So I decreased the ref voltage to {aimed_dc_link_voltage}V")
        else:
            print(f"Wrong- desired frequency was higher than the frequency now. So I decreased the ref voltage. However this resulted in greater frequency diff. So I canceled the changes and increased the ref voltage to {aimed_dc_link_voltage+2*abs_delta_voltage}V ")
            execute_command("driver_set_ref_voltage", int((aimed_dc_link_voltage+2*abs_delta_voltage)*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
            time.sleep(10)
        
    else:
        aimed_dc_link_voltage = avg_dc_link_voltage + abs_delta_voltage
        execute_command("driver_set_ref_voltage", int(aimed_dc_link_voltage*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
        time.sleep(7.5)              
        
        freq_new = float(average_executed_command(1, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100
        abs_freq_dif_new = abs(desired_frequency-freq_new)

        avg_dc_link_voltage = float(average_executed_command(1, "driver_read_Dri_DC_voltage", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/10
        if(abs(avg_dc_link_voltage-aimed_dc_link_voltage) > 12):
            print(f"Impulsive voltage change of {abs(avg_dc_link_voltage-aimed_dc_link_voltage)}V is detected. So I set voltage referecene as same with the dc line voltage : {avg_dc_link_voltage}V")
            execute_command("driver_set_ref_voltage", int(avg_dc_link_voltage*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
            return None

        if(abs_freq_dif_new<abs_freq_dif_old):
            print(f"Right- desired frequency was lower than the frequency now. So I increased the ref voltage to {aimed_dc_link_voltage}V")
        else:
            print(f"Wrong- desired frequency was lower than the frequency now. So I increased the ref voltage. However this resulted in greater frequency diff. So I canceled the changes and lowered the ref voltage to {aimed_dc_link_voltage-2*abs_delta_voltage}V ")
            execute_command("driver_set_ref_voltage", int((aimed_dc_link_voltage-2*abs_delta_voltage)*10), WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, should_raise_error)
            time.sleep(10)

    pass



