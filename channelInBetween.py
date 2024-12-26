#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Simulating Channel Impairments
# Author: Salih Karabulut
# Description: simulating channel impairments by using gnuradio
# GNU Radio version: 3.10.7.0

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq



class channelInBetween(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Simulating Channel Impairments", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Simulating Channel Impairments")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "channelInBetween")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samples_per_symbol = samples_per_symbol = 2
        self.samp_rate = samp_rate = 32000
        self.packet_len = packet_len = 1024
        self.pack_unpack_k = pack_unpack_k = 8
        self.excess_bw = excess_bw = 0.35
        self.bpsk = bpsk = digital.constellation_bpsk().base()

        ##################################################
        # Blocks
        ##################################################

        self.zeromq_sub_source_0 = zeromq.sub_source(gr.sizeof_char, 1, 'tcp://127.0.0.1:49203', 100, False, (-1), '', False)
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:49201', 100, False, (-1), '', True, True)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_MUELLER_AND_MULLER,
            samples_per_symbol,
            0.045,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_map_bb_0 = digital.map_bb([0, 1])
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=bpsk,
            differential=True,
            samples_per_symbol=samples_per_symbol,
            pre_diff_code=True,
            excess_bw=excess_bw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(bpsk)
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(pack_unpack_k)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_char*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, packet_len, "packet_len")
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "channelInBetween")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samples_per_symbol(self):
        return self.samples_per_symbol

    def set_samples_per_symbol(self, samples_per_symbol):
        self.samples_per_symbol = samples_per_symbol

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.packet_len)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.packet_len)

    def get_pack_unpack_k(self):
        return self.pack_unpack_k

    def set_pack_unpack_k(self, pack_unpack_k):
        self.pack_unpack_k = pack_unpack_k

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw

    def get_bpsk(self):
        return self.bpsk

    def set_bpsk(self, bpsk):
        self.bpsk = bpsk
        self.digital_constellation_decoder_cb_0.set_constellation(self.bpsk)




def main(top_block_cls=channelInBetween, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
