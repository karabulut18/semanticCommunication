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
        in_signal = input_items[0]
        out_signal = output_items[0]

        available_space = len(out_signal)
        total_written = 0

        # Append new input data to the buffer
        self.buffer.extend(in_signal)

        while available_space > 0:
            if self.state == 0:  # Idle
                # Check if there's enough data in the buffer to process
                if len(self.buffer) >= self.pkt_len:
                    self.state = 1  # Move to processing state
                else:
                    break  # Wait for more data

            elif self.state == 1:  # Send Preamble
                to_write = min(len(self.preamble), available_space)
                out_signal[total_written:total_written + to_write] = self.preamble[:to_write]
                total_written += to_write
                available_space -= to_write

                if to_write < len(self.preamble):
                    self.preamble = self.preamble[to_write:]  # Send remaining preamble later
                else:
                    self.state = 2  # Move to data state
                break

            elif self.state == 2:  # Send Data
                packet = self.buffer[:self.pkt_len]
                del self.buffer[:self.pkt_len]  # Remove processed data from buffer

                to_write = min(len(packet), available_space)
                out_signal[total_written:total_written + to_write] = packet[:to_write]
                self.add_item_tag(0, total_written, pmt.intern("packet_len"), pmt.from_long(len(packet)))
                total_written += to_write
                available_space -= to_write

                if len(self.buffer) < self.pkt_len:
                    self.state = 3  # Move to postamble state
                break

            elif self.state == 3:  # Send Postamble
                to_write = min(len(self.postamble), available_space)
                out_signal[total_written:total_written + to_write] = self.postamble[:to_write]
                total_written += to_write
                available_space -= to_write

                if to_write < len(self.postamble):
                    self.postamble = self.postamble[to_write:]  # Send remaining postamble later
                else:
                    self.state = 0  # Back to idle
                break

        return total_written
