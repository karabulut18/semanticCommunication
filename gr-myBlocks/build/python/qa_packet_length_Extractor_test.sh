#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir="/Users/saka/Desktop/SC/zmq_sockets/gr-myBlocks/python"
export GR_CONF_CONTROLPORT_ON=False
export PATH="/Users/saka/Desktop/SC/zmq_sockets/gr-myBlocks/build/python":$PATH
export DYLD_LIBRARY_PATH="":$DYLD_LIBRARY_PATH
export PYTHONPATH=/Users/saka/Desktop/SC/zmq_sockets/gr-myBlocks/build/swig:$PYTHONPATH
/opt/local/Library/Frameworks/Python.framework/Versions/3.9/bin/python3.9 /Users/saka/Desktop/SC/zmq_sockets/gr-myBlocks/python/qa_packet_length_Extractor.py 
