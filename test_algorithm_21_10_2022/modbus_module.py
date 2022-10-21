import time
from serial_module import write_to_port_and_get_response


write_commands = {
    "driver_run": "15,6,32,0,0,1\n",
    "driver_stop": "15,6,32,0,0,5\n",
    "driver_set_ref_voltage": "15,6,15,2,<sig_byte>,<lst_byte>\n",
    "driver_set_battery_charging_current": "16,6,0,34,<sig_byte>,<lst_byte>\n",
}
read_commands = {
    "driver_read_frequency": "15,03,17,01,00,01\n",
    "driver_read_ref_dc_voltage": "15,03,15,02,00,01\n",
    "driver_dc_link_voltage": "15,03,18,01,00,01\n",
    "pv_power": "16,04,00,04,00,01\n",
    "pv_load_power": "16,04,00,10,00,01\n",
    "pv_read_holding_register": "16,03,<sig_byte>,<lst_byte>,00,01\n"
}

latest_replies = {}


def execute_command(command=None, value=None, wait_response_seconds=1):
    # write commands
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

        return response

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
        return response

    else:
        raise Exception(f"command= {command} is not known")
def print_latest_replies():
    print("PRINTING LATEST REPLIES =====================")
    for key, value in latest_replies.items():
        print(f"{key} = {value}")
    print()