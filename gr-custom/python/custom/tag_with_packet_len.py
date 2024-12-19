#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Salih Karabulut.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import numpy as np
from gnuradio import gr
from header import Header 

class tag_with_packet_len(gr.sync_block):
    """
    A block to parse headers and add packet_len tag
    """
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="tag_with_packet_len",
            in_sig=[np.uint8],  # input data type
            out_sig=[np.uint8]  # output data type
        )
        self.header_size = Header.get_size()

    def work(self, input_items, output_items):
        in_data = input_items[0]
        out_data = output_items[0]
        consumed = 0

        while consumed + self.header_size <= len(in_data):
            header_bytes = in_data[consumed : consumed + self.header_size]
            header = Header.deserialize(header_bytes)
            packet_size = header.size

            if consumed + self.header_size + packet_size > len(in_data):
                break  # if it is incomplete

            # add packet_len
            self.add_item_tag(
                0,  # output port 
                self.nitems_written(0) + consumed,
                "packet_len", 
                packet_size
            )

            out_data[consumed : consumed + self.header_size + packet_size] = \
                in_data[consumed : consumed + self.header_size + packet_size]
            consumed += self.header_size + packet_size

        return consumed
