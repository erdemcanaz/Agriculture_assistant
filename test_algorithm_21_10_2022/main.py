from modbus_module import execute_command,print_latest_replies


while(True):
        execute_command("driver_run", None, 1)
        execute_command("driver_stop", None, 1)
        print_latest_replies()