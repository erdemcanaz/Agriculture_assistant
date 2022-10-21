from serial_module import write_to_port_and_get_response
import time
while(True):
        print(write_to_port_and_get_response('15,6,32,0,0,1\n', 0.07))