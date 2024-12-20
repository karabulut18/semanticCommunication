# semanticCommunication
a testbed for semantic communication development

# environment setup
gnuradio-companion is not working properly on conda macos

a docker container seems to be more useful

how to run docker gui on macos
https://gist.github.com/roaldnefs/fe9f36b0e8cf2890af14572c083b516c

docker setup
https://github.com/git-artes/docker-gnuradio

if you cannot run gnuradio-compaion, try add to your localip to allowed xhosts

ifconfig en0 | grep inet

xhost + <_localip>

I chnaged docker container command as:

 docker run -dit \
 --name gnuradio-container \
 --net=host \
 -e DISPLAY=host.docker.internal:0 \
 -v /tmp/.X11-unix:/tmp/.X11-unix \
 --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
 --volume <source_dir>:/home/gnuradio/persistent \
 --device /dev/snd \
 --device /dev/dri \
 --volume /dev/bus/usb:/dev/bus/usb \
 --privileged \
 --group-add=audio \
 gnuradio:3.10
