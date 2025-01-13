"""
Embedded Python Block: Byte Stream to Tagged Stream
"""

import numpy as np
from gnuradio import gr
import pmt

"""
State Definitions:
    0: Idle
    1: Send Preamble
    2: Send Data
    3: Send Postamble
"""

class blk(gr.sync_block):
    def __init__(self, Pkt_len=52):
        gr.sync_block.__init__(
            self,
            name="EPB: Byte Stream to Tagged Stream",
            in_sig=[np.uint8],  # Input stream of bytes
            out_sig=[np.uint8]  # Output stream of bytes
        )

        self.Pkt_len = Pkt_len
        self.state = 0  # Start in idle state
        self.indx = 0  # Absolute index for tagging

        # Preamble and Postamble definitions
        self.preamble = np.array([37,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93], dtype=np.uint8)
        self.preamble_len = len(self.preamble)
        self.postamble = np.array([37,85,85,85, 35,69,79,70, 85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93], dtype=np.uint8)
        self.postamble_len = len(self.postamble)

        # Internal buffer to hold incoming data
        self.buffer = bytearray()

    def work(self, input_items, output_items):
        in_stream = input_items[0]
        out_stream = output_items[0]

        available_space = len(out_stream)  # Remaining space in the output buffer
        total_written = 0  # Track how much data is written in this call

        # Add incoming data to the internal buffer
        self.buffer.extend(in_stream)

        while available_space > 0:
            if self.state == 0:  # Idle
                # If there's data in the buffer, move to the preamble state
                if len(self.buffer) > 0:
                    self.state = 1
                else:
                    break

            elif self.state == 1:  # Send Preamble
                to_write = min(self.preamble_len, available_space)
                out_stream[total_written:total_written + to_write] = self.preamble[:to_write]

                # Tag for the preamble
                self.add_item_tag(0, self.indx, pmt.intern("packet_len"), pmt.from_long(self.preamble_len))
                self.indx += to_write
                total_written += to_write
                available_space -= to_write

                # Transition to data if the preamble is fully sent
                if to_write == self.preamble_len:
                    self.state = 2

            elif self.state == 2:  # Send Data
                if len(self.buffer) == 0:
                    # No more data in the buffer, move to postamble
                    self.state = 3
                    continue

                # Take a chunk of data from the buffer
                data_chunk = self.buffer[:self.Pkt_len]
                del self.buffer[:self.Pkt_len]  # Remove processed data

                chunk_len = len(data_chunk)
                to_write = min(chunk_len, available_space)
                out_stream[total_written:total_written + to_write] = data_chunk[:to_write]

                # Tag for the data chunk
                self.add_item_tag(0, self.indx, pmt.intern("packet_len"), pmt.from_long(chunk_len))
                self.indx += to_write
                total_written += to_write
                available_space -= to_write

                # Wait for the next call if the chunk isn't fully written
                if to_write < chunk_len:
                    break

            elif self.state == 3:  # Send Postamble
                to_write = min(self.postamble_len, available_space)
                out_stream[total_written:total_written + to_write] = self.postamble[:to_write]

                # Tag for the postamble
                self.add_item_tag(0, self.indx, pmt.intern("packet_len"), pmt.from_long(self.postamble_len))
                self.indx += to_write
                total_written += to_write
                available_space -= to_write

                # Transition back to idle after sending the postamble
                if to_write == self.postamble_len:
                    self.state = 0

        return total_written

