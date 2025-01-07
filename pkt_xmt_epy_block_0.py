"""
Embedded Python Block: File Source to Tagged Stream
"""

import numpy as np
from gnuradio import gr
import time
import pmt
import os.path
import sys
import base64
from header import Header, msg_type
from text   import textMessage
from logger import LOG, LOGE, initialize_logger
from time import sleep

"""
State definitions
    0   idle
    1   send preamble
    2   send file data
    3   send file name
    4   send post filler
"""
# message queue
#messageQueue = deque()

"""
State definitions
    0   empty - idle
    <messsageSend>
        1   message send start
        2   send preamble
        3   send message
        4   send post filler
        5   message send end
"""

class blk(gr.sync_block):
    def __init__(self, FileName='None', Pkt_len=52):
        gr.sync_block.__init__(
            self,
            name='EPB: File Source to Tagged Stream',
            in_sig=None,
            out_sig=[np.uint8])
        self.FileName = FileName
        self.Pkt_len = Pkt_len
        self.state = 0      # idle state
        self.pre_count = 0
        self.indx = 0
        self._debug = 0     # debug
        self.data = ""
        initialize_logger("embedded_python_block_test")

    #    if (os.path.exists(self.FileName)):
    #        # open input file
    #        self.f_in = open (self.FileName, 'rb')
    #        self._eof = False
    #        if (self._debug):
    #            print ("File name:", self.FileName)
    #        self.state = 1
    #    else:
    #        print(self.FileName, 'does not exist')
    #        self._eof = True
    #        self.state = 0
        self.state = 1

        self.heartbeat       = "HEAERTBEAT_"
        self.heartbeat_count = 0

        self.char_list = [37,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.c_len = len (self.char_list)
        # print (self.c_len)
        self.filler = [37,85,85,85, 35,69,79,70, 85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.f_len = len (self.filler)

    def work(self, input_items, output_items):

        if (self.state == 0):
            # idle
            sleep(1)
            self.state = 1
            return (0)

        elif (self.state == 1):
            # send preamble
            if (self._debug):
                print ("state = 1", self.pre_count)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.c_len)
            self.add_item_tag(0, # Write to output port 0
                self.indx,   # Index of the tag
                key1,   # Key of the tag
                val1    # Value of the tag
                )
            self.indx += self.c_len
            i = 0
            max_length = min(self.c_len, len(self.char_list))
            while (i < max_length):
                output_items[0][i] = self.char_list[i]
                i += 1
            self.pre_count += 1
            if (self.pre_count > 64):
                self.pre_count = 0
                self.state = 2      # send msg
            return (self.c_len)

        elif (self.state == 2):
            string_buffer = self.heartbeat + str(self.heartbeat_count)
            self.heartbeat_count += 1
            heartbeatMessage = textMessage(string_buffer)
            heartbeatMessage.print_text()
            buffer = heartbeatMessage.serialize()
            buffer_size = len(buffer)
            buffer_index = 0
            while(buffer_index < buffer_size):
                b_len = 0
                if(buffer_index + self.Pkt_len > buffer_size):
                    b_len = buffer_size - buffer_index
                    self.state = 4 # after that send postamble
                else:
                    b_len = self.Pkt_len

                buff            = buffer[buffer_index : b_len]
                buffer_index    = buffer_index + b_len
                key0 = pmt.intern("packet_len")
                val0 = pmt.from_long(b_len)
                self.add_item_tag(0, # Write to output port 0
                    self.indx,   # Index of the tag
                    key0,   # Key of the tag
                    val0    # Value of the tag
                    )
                self.indx += b_len
                i = 0
                while (i < b_len):
                    output_items[0][i] = buff[i]
                    i += 1
                return (b_len)


        #elif (self.state == 3):
        #    # send file name
        #    fn_len = len (self.FileName)
        #    key1 = pmt.intern("packet_len")
        #    val1 = pmt.from_long(fn_len+8)
        #    self.add_item_tag(0, # Write to output port 0
        #        self.indx,   # Index of the tag
        #        key1,   # Key of the tag
        #        val1    # Value of the tag
        #        )
        #    self.indx += (fn_len+8)
        #    i = 0
        #    while (i < 8):
        #        output_items[0][i] = self.filler[i]
        #        i += 1
        #    j = 0
        #    while (i < (fn_len+8)):
        #        output_items[0][i] = ord(self.FileName[j])
        #        i += 1
        #        j += 1
        #    self.state = 4
        #    return (fn_len+8)

        elif (self.state == 4):
            # send post filler
            if (self._debug):
                print ("state = 4", self.pre_count)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.f_len)
            self.add_item_tag(0, # Write to output port 0
                self.indx,   # Index of the tag
                key1,   # Key of the tag
                val1    # Value of the tag
                )
            self.indx += self.f_len
            i = 0
            while (i < self.f_len):
                output_items[0][i] = self.filler[i]
                i += 1
            self.pre_count += 1
            if (self.pre_count > 16):
                self.pre_count = 0
                self.state = 0      # idle
            return (self.f_len)

        return (0)

