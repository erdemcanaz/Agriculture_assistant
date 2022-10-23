from modbus_command_module import execute_command, average_executed_command



def calculate_motor_power_watts_by_frequency(frequency):
    return (27.84392-4.6395*frequency+0.915*pow(frequency,2))

def drive_motor_at_frequency(desired_frequency): 
    WAIT_RESPONSE_SECONDS = 1
    NUMBER_OF_MAX_RETRIES = 10
    raise_error = True

    if desired_frequency == 0:
        execute_command("driver_stop", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, raise_error)
    else:
        execute_command("driver_run", None, WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES, raise_error)

    freq_initial =  float(average_executed_command(2, "driver_read_Dri_Frequency", None , WAIT_RESPONSE_SECONDS, NUMBER_OF_MAX_RETRIES))/100

    if(freq_initial >=49.5 and desired_frequency >= 49.5):
        return None

    #============================================
    #TODO
    #TODO
    #TODO    
    #============================================

    pass