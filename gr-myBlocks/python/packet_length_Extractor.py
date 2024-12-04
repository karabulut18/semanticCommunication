import struct
import numpy as np
from gnuradio import gr

from message.msg_protocol import Header

class packet_length_Extractor(gr.sync_block):
    def __init__(self, message_size):
        gr.sync_block.__init__(self,
            name="Custom Message Parser",
            in_sig=[np.uint8],
            out_sig=[np.uint8])
        self.message_size = message_size

    def work(self, input_items, output_items):
        in_0 = input_items[0]
        out_0 = output_items[0]

        # Ensure enough data is available for at least the header
        if len(in_0) < Header.get_size():
            return 0

        # Extract the header
        header_data = in_0[:Header.get_size()]
        header = Header.deserialize(header_data)

        # Ensure enough data is available for the entire message
        total_message_size = Header.get_size() + header.size
        if len(in_0) < total_message_size:
            return 0

        # Extract the message data based on header size
        message_data = in_0[Header.get_size():total_message_size]

        # Output the message data
        out_0[:header.size] = message_data

        return header.size
