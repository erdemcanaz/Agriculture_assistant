
import serial
import datetime
import time


serial_port = serial.Serial(port='COM8', baudrate=9600, timeout=.1)
#Arduino uno restarts itself whenever a serial connection is established. So let it recover.
time.sleep(3)


write_commands= {
    "driver_run":"15,6,32,0,0,1\n",
    "driver_stop":"15,6,32,0,0,5\n",
    "driver_enable_pv_mode":"15,6,15,0,0,1\n",
    "driver_enable_voltage_reference_mode":"15,6,15,1,0,0\n",
    "driver_set_ref_voltage":"15,6,15,2,<sig_byte>,<lst_byte>\n",
    "driver_set_battery_charging_current":"16,6,0,34,<sig_byte>,<lst_byte>\n",
}

read_commands= {
    "driver_read_frequency"      :"15,03,17,01,00,01\n",
    "driver_read_ref_dc_voltage" :"15,03,15,02,00,01\n",
    "driver_dc_link_voltage"     :"15,03,18,01,00,01\n",
    "pv_power"                   :"16,04,00,04,00,01\n",
    "pv_load_power"              :"16,04,00,10,00,01\n",
    "pv_read_holding_register"    :"16,03,<sig_byte>,<lst_byte>,00,01\n"
}

replies = {
    "driver_run":{
        "value":None,
        "time_stamp": None
    },
    "driver_stop":{
        "value":None,
        "time_stamp": None
    },
    "driver_read_frequency":{
        "value":None,
        "time_stamp": None
    },
    "driver_read_ref_dc_voltage":{
        "value":None,
        "time_stamp": None
    },
    "driver_dc_link_voltage":{
        "value":None,
        "time_stamp": None
    },
    "driver_set_ref_voltage":{
        "value":None,
        "time_stamp": None
    },
    "pv_power":{
        "value":None,
        "time_stamp": None
    },
    "pv_load_power":{
        "value":None,
        "time_stamp": None
    },
    "pv_read_holding_register":{
        "value":None,
        "time_stamp": None
    },
    "driver_set_battery_charging_current":{
        "value":None,
        "time_stamp": None
    }
}

def execute_and_get_reply(command_key, is_write_command, value, wait_response_seconds, try_until_having_response):
    command_to_execute = write_commands[command_key] if is_write_command else read_commands[command_key]

    if(value != None):
        #value is 16 bit unsigned integer
        value = int(value)
        sig_byte = value>>8
        lst_byte = value%256

        command_to_execute = command_to_execute.replace("<sig_byte>",str(sig_byte))
        command_to_execute =command_to_execute.replace("<lst_byte>",str(lst_byte))

    serial_port.write(command_to_execute.encode('utf-8'))

    time.sleep(wait_response_seconds)
    buffer_str = serial_port.read_until('\n').decode('utf-8')   

    if buffer_str != "":
       replies[command_key]["value"]=int(buffer_str)   
       replies[command_key]["time_stamp"]=datetime.datetime.now() 
       return( replies[command_key]["value"] )
    else:
        if(try_until_having_response):
            return execute_and_get_reply(command_key, is_write_command, value, wait_response_seconds, try_until_having_response)    
        else:
            return None

# ======================================
def calculate_average_frequency(step_count, wait_response_seconds):
    jump_condition = 1000
    freq_sum = 0
    last_frequency = None   
    points = [] 
    i = 0
    while i < step_count:
        new_frequency = execute_and_get_reply('driver_read_frequency',False, None, wait_response_seconds, False)
        points.append(new_frequency)

        if(last_frequency == None and new_frequency != None):
            if(new_frequency != None):
                last_frequency = new_frequency
            else:
                continue      

        if(new_frequency != None):  
            i = i + 1           

            if (abs(new_frequency - last_frequency)) > jump_condition:
                    i = 0
                    freq_sum = 0
                    print("frequency showed impulsive behaviour, re-averaging")
            freq_sum = freq_sum + new_frequency
            last_frequency = new_frequency
    
    return [(freq_sum/step_count), points]

def calculate_average_dc_link_from_driver(step_count, wait_response_seconds):
    jump_condition = 100
    voltage_sum = 0
    last_voltage = None
    points = []    
    i = 0
    while i < step_count:
        new_voltage= execute_and_get_reply('driver_dc_link_voltage',False, None, wait_response_seconds, False)
        points.append(new_voltage)
        if(last_voltage == None and new_voltage != None):
            if(new_voltage != None):
                last_voltage = new_voltage
            else:
                continue      

        if(new_voltage != None):  
            i = i + 1           

            if (abs(new_voltage - last_voltage)) > jump_condition:
                    i = 0
                    voltage_sum = 0
                    print("voltage showed impulsive behaviour, re-averaging")
            voltage_sum = voltage_sum + new_voltage
            last_voltage = new_voltage
    
    return [ (voltage_sum/step_count),  points]        

def drive_motor(desired_frequency): 
    freq_now = calculate_average_frequency(4,0.25)[0]
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


def map_watt_to_frequency(frequency_now):
    return (27.84392-4.6395*frequency_now+0.915*pow(frequency_now,2))

while True:
    measured_pv_power =   execute_and_get_reply('pv_power',False, None, 0.4, True)
    print("PV POWER:".ljust(30), measured_pv_power/10, "WATTS")


    measured_pv_load_power = execute_and_get_reply('pv_load_power',False, None, 0.4, True)
    print("PV LOAD POWER:".ljust(30), measured_pv_load_power/10, "WATTS")   
   
    calculated_battery_charging_power = (measured_pv_power-measured_pv_load_power)
    print("CALCULATED CHARGING POWER:".ljust(30), calculated_battery_charging_power/10, "WATTS")

    print("===")

    read_driver_reference_frequency = execute_and_get_reply('driver_read_ref_dc_voltage',False, None,  0.25, True)
    

    driver_frequency =  execute_and_get_reply('driver_read_frequency',False, None, 0.25, True)
    print("MOTOR FREQUENCY:".ljust(30), driver_frequency/100, "HZ")

    predicted_driver_power = map_watt_to_frequency(driver_frequency/100)
    print("PREDICTED MOTOR POWER:".ljust(30), int(predicted_driver_power), "WATTS")

    driver_dc_link_voltage = execute_and_get_reply('driver_dc_link_voltage',False, None, 0.25, True)
    print("DRIVER DC LINK VOLTAGE".ljust(30), driver_dc_link_voltage/10, "V")

    print("===")
    drive_motor(0)
    
    print("===========================")
    
    # execute_and_get_reply('driver_read_ref_dc_voltage',False, None,  0.25)
   
    

