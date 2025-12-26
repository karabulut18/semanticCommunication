# Semantic Communication Testbed

A flexible, modular testbed for developing and testing Semantic Communication algorithms. This project bridges high-level application logic (Python) with low-level physical layer simulations (GNU Radio) using a ZeroMQ-based architecture.

## 🚀 Overview

This repository provides an infrastructure to transport files through a simulated wireless channel. It decouples the "Semantic Agent" (Application Layer) from the "Channel Simulator" (Physical Layer) using TCP sockets (ZeroMQ).

**Core Architecture:**
`[Sender App (Python)] --> [ZMQ PUB] --> [GNU Radio Transmitter] --(Channel)--> [GNU Radio Receiver] --> [ZMQ SUB] --> [Receiver App (Python)]`

This architecture provides a flexible foundation, allowing for the future integration of an encoder-decoder model between the `filePublisher` and `fileSubscriber`.

## 📂 Repository Structure

### Python Application Layer
- **`filePublisher.py`**: Reads files from disk and sends them to the `pkt_xmt` block via ZMQ.
- **`fileSubscriber.py`**: Receives file messages from the `pkt_rcv` block and reconstructs them on disk.
- **`file_transfer_unit.py`**: Logic for chunking files, managing metadata, and handling file I/O.
- **`myers_diff.py`**: Implements the [Myers' Diff](http://www.xmailserver.org/diff2.pdf) algorithm for binary similarity comparison between sent and received files.

### GNU Radio Physical Layer (`simulationChannel/`)
The simulation channel consists of three main components:
1.  **`pkt_xmt.grc`**: Converts a byte stream (from ZMQ Publisher source) into a BPSK signal. It has been modified from standard examples to use a "Byte to Tagged Stream" approach for better abstraction.
2.  **`chan_loopback.grc`**: Simulates channel impairments with configurable noise voltage to emulate real-world conditions.
3.  **`pkt_rcv.grc`**: Demodulates the BPSK signal back into a byte stream and forwards it via ZMQ Publisher Sink.

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.8+**
- **GNU Radio 3.8+** (or use the Docker setup below)
- **ZeroMQ** (`pyzmq`)

### macOS / Linux Setup (Docker Recommended)
Running GNU Radio natively on macOS can be challenging. It is highly recommended to use a Docker container for the signal processing layer.

1.  **Install Docker & XQuartz** (for GUI support on macOS).
2.  **Run Container**:
    ```bash
    docker run -dit \
      --name gnuradio-container \
      --net=host \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
      --volume $(pwd):/home/gnuradio/persistent \
      marriedgorillas/gnuradio-non-root
    ```

## 🚦 Usage

1.  **Start the Channel simulation**:
    Open `simulationChannel/pkt_xmt.grc` in GNU Radio Companion and run the flowgraph.

2.  **Start the Receiver**:
    ```bash
    python3 fileSubscriber.py --port 5555 --file_directory ./receiver_side_files
    ```

3.  **Start the Sender**:
    ```bash
    python3 filePublisher.py --port 5555 --file_directory ./sender_side_files
    ```

4.  **Compare Results**:
    ```bash
    python3 myers_diff.py ./sender_side_files/test.txt ./receiver_side_files/test.txt
    ```

## 🔮 Future Work & Concepts

The original vision for this project was to implement a **Semantic Autoencoder**:
- **Encoder**: Use **BLIP-2** to generate dense semantic captions of images.
- **Decoder**: Use **Segment Anything** or Stable Diffusion to reconstruct images from received semantic tokens.
This infrastructure is designed to carry those semantic tokens, enabling extreme compression for specific tasks.

## ⚠️ Known Limitations
- **Platform**: Native macOS support for GNU Radio is experimental.
- **Protocol**: Custom framing currently uses fixed padding.
- **Flow Control**: Uses basic sleep timers; production use requires robust ARQ.
