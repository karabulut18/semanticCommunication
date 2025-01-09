"""
Embedded Python Block: ZMQ data to Tagged Stream
"""

import numpy as np
from gnuradio import gr
import time
import pmt
import os.path
import sys
import base64

"""
State definitions
    0   idle (wait for the message)
    1   send preamble
    2   send data
    3   send post filler
"""

class blk(gr.sync_block):
    def __init__(self, Pkt_len=52, debug_active=False):
        gr.sync_block.__init__(
            self,
            name='ZMQ Data to Tagged Stream',
            in_sig=[np.uint8],
            out_sig=[np.uint8])
        self.pkt_len    = Pkt_len
        self.state      = 0 # idle state
        self._debug     = debug_active
        self.state = 0

        self.preamble = [37,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        # print (self.c_len)
        self.filler = [37,85,85,85, 35,69,79,70, 85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.buffer = []


    def work(self, input_items, output_items):
        in_signal   = input_items[0]
        out_signal  = output_items[0]

        available_space = len(out_signal)
        total_written = 0

        self.buffer.extend(in_signal)

        while available_space > 0:
            if self.state == 0:  # Idle
                if len(self.buffer) >= self.pkt_len:
                    self.state = 1  # Move to preamble
                else:
                    break

            elif self.state == 1:  # Send Preamble
                to_write = min(len(self.preamble), available_space)
                output_items[0][:to_write] = self.preamble[:to_write]
                total_written   += to_write
                available_space -= to_write
                self.indx       += to_write

                if to_write < len(self.preamble):
                    self.preamble = self.preamble[to_write:]  # Send remaining preamble next
                else:
                    self.state = 2  # Move to data
                break

            elif self.state == 2:  # Send Data
                if self.data_index >= len(self.current_data):
                    self.state = 3  # Data complete, move to postamble
                    break

                chunk = self.current_data[self.data_index:self.data_index + self.pkt_len]
                to_write = min(len(chunk), available_space)
                output_items[0][:to_write] = chunk[:to_write]
                self.add_item_tag(0, self.indx, pmt.intern("packet_len"), pmt.from_long(to_write))
                self.data_index += to_write
                total_written   += to_write
                available_space -= to_write
                self.indx       += to_write

                if self.data_index >= len(self.current_data):
                    self.state = 3  # All data sent
                break

            elif self.state == 3:  # Send Postamble
                to_write = min(len(self.postamble), available_space)
                output_items[0][:to_write] = self.postamble[:to_write]
                total_written   += to_writenn
                available_space -= to_write
                self.indx       += to_write

                if to_write < len(self.postamble):
                    self.postamble = self.postamble[to_write:]  # Send remaining postamble next
                else:
                    self.state = 0  # Back to idle
                break

        return total_written
