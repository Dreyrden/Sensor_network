"""
Remote Sensing Base communication protocol.

Dependencies:
    apscheduler - http://pythonhosted.org/APScheduler/
    xbee python library - https://code.google.com/p/python-xbee/

    Network Stress Test

"""

from xbee import ZigBee
import serial

# Implementation of logging library required
#import logging
#import datetime
import time


import logging
logging.basicConfig(filename='example.log', setLevel=logging.INFO)

time.clock()
# Serial Port Information
PORT = 'COM5'
BAUD_RATE = 9600

# XBee Address Information
BROADCAST = b'\x00\x00\x00\x00\x00\x00\xFF\xFF'
# This is the 'I don't know' 16 bit address
UNKNOWN = b'\xFF\xFE'

# Store all network keys in list, retreive using index
# network_long = ['\x00\x00\x00\x00\x00\x00\xff\xff']  # etc
# network_short = ['\x00\x00']  # etc

'''Function Definitions'''

def stresspacket(number, width=8):
        """
        Generates a list of data payloads to be sent with unique values.
        In string format, with appended 0's on the front of generated number.

        Inputs:         number          Number of unique payloads generated
                        width           Width of the outputted strings (default = 8)

        Outputs:        stresslist      List of strings with required format
        """
        stresslist = list(map(str, list(range(number))))
        stresslist = ['{:0>{swidth}s}'.format(x, swidth=width).encode('utf-8') for x in stresslist]
        return stresslist


def message_received_stress(data):
        """
        Call back Function for stresstest. Prints value immediately.
        """
        logging.info('Received Packet at: ' + str(time.clock()))

        if data['id'] == 'tx_status':
            if ord(data['deliver_status']) != 0:
                logging.info('Transmit error = ')
                logging.info(data['deliver_status'].encode('hex'))

        # Determine if received packet is a data packet
        elif data['id'] == 'rx':
            logging.info(data['rf_data'])
            # len(rxList)  # Do things
            # Detemine if received packet is an undetermined XBee frame
        else:
            logging.info('Unimplemented XBee frame type' + data['id'])

def sendPacket(address_long, address_short, payload):
        """
        Sends a Packet of data to an XBee.

 	Inputs:     address_long - 64bit destination XBee Address
                    address_short - 16bit destination XBee Address
                    payload - Information to be sent to payload
        """
        #logging.info(len(address_long))
        #logging.info(len(address_short))
        logging.info('Sent Packet at: ' + str(time.clock()))
        xbee.send('tx',
                  dest_addr_long=address_long,
                  dest_addr=address_short,
                  data=payload
                  )

# Generate Stress Packets
print('generating stress packets')
sp = stresspacket(1000,8)

# Open XBee Serial Port
ser = serial.Serial(PORT, BAUD_RATE)

# Create XBee library API object, which spawns a new thread
xbee = ZigBee(ser, callback=message_received_stress, escaped=True)


############ SEND LOOP ############

print('sending stress packets')
for x in sp:
        sendPacket(BROADCAST, UNKNOWN, x)
        # time.delay(0.001)

# Main thread handles received packets
'''while True:
    try:
        print('try')
    except KeyboardInterrupt:
        break
'''

# halt() must be called before closing the serial port in order to ensure
#  proper thread shutdown
xbee.halt()
ser.close()
