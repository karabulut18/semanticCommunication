# Testbed for Semantic Communication 
This repo is an example of building a testbed for semantic communication development by using gnu-radio.

## Environment setup
In order to run on macos environment follow Setup steps.

Go to the links provided below.

[gnuradio docker setup](https://github.com/git-artes/docker-gnuradio)

[how to open docker gui on macos](https://gist.github.com/roaldnefs/fe9f36b0e8cf2890af14572c083b516c)

> xhost + localhost

if localhost does not work, try to add your localip to allowed xhosts
> ifconfig en0 | grep inet

> xhost + <_localip>

I chnaged docker container command as:
 > docker run -dit \
 > --name gnuradio-container \
 > --net=host \
 > -e DISPLAY=host.docker.internal:0 \
 > -v /tmp/.X11-unix:/tmp/.X11-unix \
 > --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
 > --volume <source_dir>:/home/gnuradio/persistent \
 > --device /dev/snd \
 > --device /dev/dri \
 > --volume /dev/bus/usb:/dev/bus/usb \
 > --privileged \
 > --group-add=audio \
 > <_container tag>

# Channel impairment simulation graph

This simulation channel consists of three components: pkt_xmt, chan_loopback, and pkt_rcv.

1- pkt_xmt: This component converts a byte stream into a BPSK signal and sends a preamble, enabling synchronization at the receiver (pkt_rcv). In the original example, the EPB: File Source to Tagged Stream block reads files, appends them with a pkt_len tag, and sends the preamble. This block has been modified to integrate with a filePublisher for better abstraction, simplifying the implementation of encoder-decoder models. The updated block is named EPB: Byte to Tagged Stream. The pkt_xmt now receives messages via a ZMQ Publisher (zmq_pub) source block and converts them to a BPSK signal.

2- chan_loopback: This flowgraph allows for the simulation of channel impairments. It includes a configurable noise voltage parameter to emulate real-world channel conditions.

3- pkt_rcv: This component converts the BPSK signal back into a byte stream and publishes the messages using a ZMQ Publisher Sink (zmq_pub_sink) block.

The original example provided by Barry Duggan: [file transfer using packet and BPSK](https://wiki.gnuradio.org/index.php?title=File_transfer_using_Packet_and_BPSK).

# File Transfer Sytem
The file transfer system consists of two parts: filePublisher and fileSubscriber.

1- filePublisher: This component reads files from disk and sends them to the pkt_xmt for further processing.

2- fileSubscriber: This component receives file messages from the pkt_rcv and writes them back to disk.

This architecture provides a flexible foundation, allowing for the future integration of an encoder-decoder model between the filePublisher and fileSubscriber.


# Result Comparision
For similarity check [myers' diff](http://www.xmailserver.org/diff2.pdf) algrotihm has been used. 



