import time
import datetime
from serial_module import write_to_port_and_get_response

IS_PRINT_COMMAND_EXECUTED = True
IS_PRINT_NUMBER_OF_RETRIES = True
IS_PRINT_VALUE = True
IS_PRINT_RESPONSE = True

write_commands = {    
    #driver related commands
    "driver_enable_PV_mode":"15,6,15,0,0,1\n",
    "driver_enable_voltage_reference_control_mode":"15,6,15,1,0,0\n",
    "driver_enable_pv_input":"15,6,15,32,0,2\n",
    "driver_select_SVPWM_control":"15,6,0,0,0,2\n",
    "driver_select_communication_running_command_channel":"15,6,0,1,0,2\n",
    "driver_select_deceleration_to_stop":"15,6,1,8,0,0\n",
    "driver_select_motor_type_as_asynchronous" : "15,6,2,0,0,0\n",
    "driver_set_rated_power_2_2kW": "15,6,2,1,8,152\n",
    "driver_set_rated_frequency_50Hz": "15,6,2,2,19,136\n",
    "driver_set_rated_speed_2870rpm": "15,6,2,3,11,54\n",
    "driver_set_rated_voltage_220V": "15,6,2,4,0,220\n",
    "driver_set_rated_current_13_8A":"15,6,2,5,0,138\n",
    "driver_set_the_maximum_frequency_50Hz":"15,6,0,3,19,136\n",
    "driver_set_upper_limit_frequency_50Hz":"15,6,0,4,19,136\n",
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
latest_replies = {}

def execute_command(command=None, value=None, wait_response_seconds=1, number_of_retries_allowed=1, raise_exception=True):
    

    number_of_retries = 0
    while number_of_retries < number_of_retries_allowed:
        if(IS_PRINT_COMMAND_EXECUTED == True):
            print(str(datetime.datetime.now()) +f":{number_of_retries}/{number_of_retries_allowed} command-> {command}: ")
            if(IS_PRINT_NUMBER_OF_RETRIES == True):
                print(f"number of retries: {number_of_retries}/{number_of_retries_allowed}, raise exception = {raise_exception}")
            if(IS_PRINT_VALUE == True):
                print(f"value = {value}")

        if command in write_commands:
            sig_byte = None
            lst_byte = None
            if isinstance(value, int):
                if (value >= 65536):
                    raise Exception(
                        f"execute_command: value should be less than 65536, but value={value}")
                elif (value < 0):
                    raise Exception(
                        f"execute_command: value should be positive integer, but value={value}")

                sig_byte = value >> 8
                lst_byte = value & 0xFF

                command_to_execute = command.replace("<sig_byte>", str(sig_byte))
                command_to_execute = command_to_execute.replace(
                    "<lst_byte>", str(lst_byte))

            response = write_to_port_and_get_response(command, wait_response_seconds)

            #save response to latest_replies
            if (isinstance(response, str)):
                reply_dict = {
                    "str_response": response,
                    "unix_time_stamp": time.time()

                }
                if (command in latest_replies):
                    latest_replies[command] = reply_dict
                else:
                    latest_replies.setdefault(command, reply_dict)
                
                if (IS_PRINT_RESPONSE == True):
                    print(f"response = {response}")
                return response
            else:
                number_of_retries+=1
            
        elif (command in read_commands):
            response = write_to_port_and_get_response(
                command, wait_response_seconds)
            
            #save response to latest_replies
            if (isinstance(response, str)):
                reply_dict = {
                    "str_response": response,
                    "unix_time_stamp": time.time()

                }
                if (command in latest_replies):
                    latest_replies[command] = reply_dict
                else:
                    latest_replies.setdefault(command, reply_dict)
                if (IS_PRINT_RESPONSE == True):
                    print(f"response = {response}")
                return response
            else:
                number_of_retries+=1

        else:
            raise Exception(f"command= {command} is not known")
    
    if(raise_exception == True):
        raise Exception(f"execute_command: command= {command} could not get response after {number_of_retries_allowed} retries")
def average_executed_command( number_of_averaging=3, command=None, value=None, wait_response_seconds=1, number_of_retries_allowed=5):
    counter = 0
    sum_float = 0
    while counter < number_of_averaging:
        response_str = execute_command(command, value, wait_response_seconds, number_of_retries_allowed, raise_exception = True)
        response_float = float(response_str)
        sum_float += response_float
        counter +=1
    return sum_float/number_of_averaging


def print_latest_replies():
    print("PRINTING LATEST REPLIES =====================")
    for key, value in latest_replies.items():
        print(f"{key} = {value}")
    print()