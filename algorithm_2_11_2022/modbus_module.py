from serial_module import write_to_port_and_get_response
from logger_module import  append_to_txt_file

write_commands = {    
    #driver related commands
    "driver_enable_PV_mode":"15,6,15,0,0,1\n",
    "driver_enable_voltage_reference_control_mode":"15,6,15,1,0,0\n",
    "driver_enable_pv_input":"15,6,15,32,0,2\n",
    "driver_select_SVPWM_control":"15,6,0,0,0,2\n",
    "driver_select_communication_running_command_channel":"15,6,0,1,0,2\n",
    "driver_select_deceleration_to_stop":"15,6,1,8,0,0\n",
    "driver_select_motor_type_as_asynchronous" : "15,6,2,0,0,0\n",
    "driver_set_rated_power_2_2kW": "15,6,2,1,0,22\n",
    "driver_set_rated_frequency_50Hz": "15,6,2,2,19,136\n",
    "driver_set_rated_speed_2870rpm": "15,6,2,3,11,54\n",
    "driver_set_rated_voltage_220V": "15,6,2,4,0,220\n",
    "driver_set_rated_current_13_8A":"15,6,2,5,0,138\n",
    "driver_set_the_maximum_frequency_50Hz":"15,6,0,3,19,136\n",
    "driver_set_upper_limit_frequency_50Hz":"15,6,0,4,19,134\n",
    "driver_set_lower_limit_frequency_0Hz":"15,6,0,5,0,0\n",

    "driver_run": "15,6,32,0,0,1\n",
    "driver_stop": "15,6,32,0,0,5\n",    
    "driver_set_ref_voltage": "15,6,15,2,<sig_byte>,<lst_byte>\n",

    #inverter related commands
    "inverter_set_Inv_BESS_Current_Ref": "16,6,0,34,<sig_byte>,<lst_byte>\n",
}
read_commands = {
    "driver_read_Dri_DC_voltage": "15,03,18,01,00,01\n",
    "driver_read_Dri_Frequency": "15,03,17,01,00,01\n",

    "inverter_read_Inv_PV_Power": "16,04,00,04,00,01\n",
    "inverter_read_Inv_Load_Power": "16,04,00,10,00,01\n",
    "inverter_read_Inv_BESS_Voltage": "16,04,00,17,00,01\n",
    


    "driver_read_ref_dc_voltage": "15,03,15,02,00,01\n",
    "pv_read_holding_register": "16,03,<sig_byte>,<lst_byte>,00,01\n"
}

def execute_command(command_key=None, value=None, wait_response_seconds=1, is_empty_response_accepted=False, number_of_retries_on_empty_response = 3, timeout_seconds=30):
    command_to_execute = None
    

    if command_key in write_commands:
        command_to_execute = write_commands[command_key]
        if value is not None:
            if(value < 0 or value > 65535):
                raise Exception("value must be between 0 and 65535")                
            value = int(value)
            sig_byte = value >> 8
            lst_byte = value & 0xFF
            command_to_execute = command_to_execute.replace("<sig_byte>", str(sig_byte))
            command_to_execute = command_to_execute.replace("<lst_byte>", str(lst_byte))
            write_to_port_and_get_response()

    elif command_key in read_commands:
        command_to_execute = read_commands[command_key]
    else:
        raise Exception("command not found")

    response = write_to_port_and_get_response(str_data_to_write=command_to_execute, wait_response_seconds=wait_response_seconds, is_empty_response_accepted=is_empty_response_accepted, number_of_retries_on_empty_response = number_of_retries_on_empty_response, timeout_seconds=timeout_seconds)
    data = "command_key: "+str(command_key) +" command_to_execute: "+ str(command_to_execute)+ " value: " + str(value)+ " response: " + str(response)
    append_to_txt_file("executed_commands", data, append_datetime_to_data=True)
    return response

def average_executed_command(command_key=None, value=None, number_of_averaging = 1,  wait_response_seconds=1, is_empty_response_accepted=False, number_of_retries_on_empty_response = 3, timeout_seconds=30):
    counter = 0
    sum_float = 0
    while counter < number_of_averaging:
        response_str = execute_command(command_key, value = value, wait_response_seconds=wait_response_seconds, is_empty_response_accepted=is_empty_response_accepted, number_of_retries_on_empty_response = number_of_retries_on_empty_response, timeout_seconds=timeout_seconds)
        response_float = float(response_str)
        sum_float += response_float
        counter +=1
    return sum_float/number_of_averaging


# execute_command("driver_read_ref_dc_voltage")
# rslt = average_executed_command("driver_read_ref_dc_voltage", value = None, number_of_averaging = 10)
# print(rslt)

