import time
from modbus_module import execute_command, average_executed_command


def calculate_motor_power_watts_by_frequency(frequency):
    return (27.84392-4.6395*frequency+0.915*pow(frequency,2))

def drive_motor_at_frequency(desired_frequency):
    DC_LINK_STEP_VOLTS = 4
    TRANSIENT_TIME_SECONDS = 7.5
    RECOVERY_TIME_SECONDS = 10

    freq_initial = None
    if desired_frequency <= 0:
        execute_command(command_key="driver_stop", value=None)
        return None
    else:
        execute_command(command_key="driver_run", value=None)
        freq_initial = float(average_executed_command("driver_read_Dri_Frequency", number_of_averaging = 1))/100
        if(freq_initial >=49.7 and desired_frequency >= 49.7):
            print("The frequency is already at the maximum. So I will not change it")
            return None

    
    delta_dc_link_voltage = DC_LINK_STEP_VOLTS
    delta_dc_link_voltage = -delta_dc_link_voltage if desired_frequency > freq_initial else delta_dc_link_voltage

    abs_freq_dif_old = abs(desired_frequency-freq_initial)
    avg_dc_link_voltage = float(average_executed_command("driver_read_Dri_DC_voltage", number_of_averaging = 1, value = None))/10
    
    aimed_dc_link_voltage = avg_dc_link_voltage + delta_dc_link_voltage
    execute_command(command_key="driver_set_ref_voltage", value= 10*(aimed_dc_link_voltage+delta_dc_link_voltage))
    time.sleep(TRANSIENT_TIME_SECONDS)
    freq_new  = float(average_executed_command("driver_read_Dri_Frequency", number_of_averaging = 1))/100
    abs_freq_dif_new = abs(desired_frequency-freq_new)

    avg_dc_link_voltage = float(average_executed_command("driver_read_Dri_DC_voltage", number_of_averaging = 1))/10
    if(abs(avg_dc_link_voltage-aimed_dc_link_voltage) > 12):
            print(f"Impulsive voltage change of {abs(avg_dc_link_voltage-aimed_dc_link_voltage)}V is detected. So I set voltage referecene as same with the dc line voltage : {avg_dc_link_voltage}V")
            execute_command(command_key="driver_set_ref_voltage", value= 10*(avg_dc_link_voltage))
            time.sleep(RECOVERY_TIME_SECONDS)
            return None
    
    if(abs_freq_dif_new<abs_freq_dif_old):
            print(f"Right- desired frequency was higher than the frequency now. So I decreased the ref voltage to {aimed_dc_link_voltage}V")
    else:
            print(f"Wrong- desired frequency was higher than the frequency now. So I decreased the ref voltage. However this resulted in greater frequency diff. So I canceled the changes and increased the ref voltage to {aimed_dc_link_voltage+2*delta_dc_link_voltage}V ")
            execute_command(command_key="driver_set_ref_voltage", value= 10*(aimed_dc_link_voltage-2*delta_dc_link_voltage))
            time.sleep(RECOVERY_TIME_SECONDS)





