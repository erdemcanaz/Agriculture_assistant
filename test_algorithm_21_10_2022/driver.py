from modbus_command_module import execute_command, average_executed_command

def calculate_motor_power_watts_by_frequency(frequency):
    return (27.84392-4.6395*frequency+0.915*pow(frequency,2))

def drive_motor(desired_frequency): 
    freq_now = average_executed_command()
    
    abs_delta_voltage = 100 if freq_now < 1500 else 30

    if(desired_frequency >0 and desired_frequency <51000):
        execute_and_get_reply("driver_run", True, None, 0.25, True)
    else:
        execute_and_get_reply("driver_stop", True, None, 0.25, True)
        return None
    

    if(desired_frequency >= freq_now):
        #assumption               
        avg_freq_old= calculate_average_frequency(4,0.25)[0]    
        abs_freq_dif_old = abs(desired_frequency-avg_freq_old)        
        avg_dc_link_voltage = calculate_average_dc_link_from_driver(4,0.25)[0]
        execute_and_get_reply('driver_set_ref_voltage', True, (avg_dc_link_voltage - abs_delta_voltage), 0.25, True)
        
        #---------
        time.sleep(5)
        #---------

        #correction
        avg_freq_new = calculate_average_frequency(4,0.25)[0]    
        abs_freq_dif_new = abs(desired_frequency-avg_freq_new)

        if(abs_freq_dif_new <= abs_freq_dif_old):      
            print("Right- desired frequency was higher than the frequency now. So I decreased the ref voltage")
        else:
            print("Wrong- desired frequency was higher than the frequency now. So I decreased the ref voltage. However this resulted in higher frequency diff. So I canceled the changes ")
            execute_and_get_reply('driver_set_ref_voltage', True, (avg_dc_link_voltage + 2 * abs_delta_voltage), 0.25,True)
            time.sleep(10)
    else:
        #assumption               
        avg_freq_old= calculate_average_frequency(4,0.25)[0]    
        abs_freq_dif_old = abs(desired_frequency-avg_freq_old)        
        avg_dc_link_voltage = calculate_average_dc_link_from_driver(4,0.25)[0]
        execute_and_get_reply('driver_set_ref_voltage', True, (avg_dc_link_voltage + abs_delta_voltage), 0.25, True)
        
        #---------
        time.sleep(5)
        #---------

        #correction
        avg_freq_new = calculate_average_frequency(4,0.25)[0]    
        abs_freq_dif_new = abs(desired_frequency-avg_freq_new)

        if(abs_freq_dif_new <= abs_freq_dif_old):      
            print("Right- desired frequency was lower than the frequency now. So I increased the ref voltage")
        else:
            print("Wrong- desired frequency was lower than the frequency now. So I increased the ref voltage. However this resulted in higher frequency diff. So I canceled the changes ")
            execute_and_get_reply('driver_set_ref_voltage', True, (avg_dc_link_voltage - 2 * abs_delta_voltage), 0.25,True)
            time.sleep(10)