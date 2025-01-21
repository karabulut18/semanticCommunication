# Testbed for Semantic Communication 
This repo is an example of building a testbed for semantic communication development by using gnu-radio.

## environment setup (Optional)
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
[file transfer using packet and BPSK](https://wiki.gnuradio.org/index.php?title=File_transfer_using_Packet_and_BPSK)

EPB: File Source to Tagged Stream block is altered to integrate with the filePublisher in pkt_xmt.grc
A Zmq sub source is added and EPB: Byte to Tagged Stream block is connected to it.

## Similarity Check
[myers' diff](https://www.nathaniel.ai/myers-diff/) algrotihm has been used



