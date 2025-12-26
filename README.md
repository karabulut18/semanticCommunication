# Semantic Communication Testbed

A flexible, modular testbed for developing and testing Semantic Communication algorithms. This project bridges high-level application logic (Python) with low-level physical layer simulations (GNU Radio) using a ZeroMQ-based architecture.

## 🚀 Overview

This repository provides an infrastructure to transport files through a simulated wireless channel. It decouples the "Semantic Agent" (Application Layer) from the "Channel Simulator" (Physical Layer) using TCP sockets (ZeroMQ).

**Core Architecture:**
`[Sender App (Python)] --> [ZMQ PUB] --> [GNU Radio Transmitter] --(Channel)--> [GNU Radio Receiver] --> [ZMQ SUB] --> [Receiver App (Python)]`

### Key Features
- **Decoupled Design**: Run your AI/ML models in Python without being tightly bound to GNU Radio's scheduler.
- **Robust Protocol**: Custom byte-level framing protocol for file metadata and content.
- **Impairment Simulation**: Uses GNU Radio to simulate channel noise, fading, and packet loss.
- **Flow Control**: Basic flow control mechanisms to handle backpressure between layers.

## 📂 Repository Structure

- **`filePublisher.py`**: The "Sender" application. Reads files, packetizes them (Metadata/Content), and publishes to the channel.
- **`fileSubscriber.py`**: The "Receiver" application. Listens for incoming packets, reconstructs files, and saves them to disk.
- **`file_transfer_unit.py`**: Logic for chunking files, managing state, and handling file I/O.
- **`simulationChannel/`**: Contains the GNU Radio Companion (`.grc`) flowgraphs.
  - `pkt_xmt.grc`: Transmitter flowgraph (accepts ZMQ, modulates, adds channel effects).
  - `pkt_rcv.grc`: Receiver flowgraph (demodulates, forwards to ZMQ).
- **`sender_side_files/`** & **`receiver_side_files/`**: default directories for input/output files.

## 🛠️ Setup & Installation

### Prerequisities
- **Python 3.8+**
- **GNU Radio 3.8+** (or use the Docker setup below)
- **ZeroMQ** (`pyzmq`)

### macOS Setup (Docker Recommended)
Running GNU Radio natively on macOS can be challenging (drivers, X11, etc.). It is recommended to use a Docker container.

1.  **Install Docker & XQuartz** (for GUI support).
2.  **Pull the Image**:
    ```bash
    docker pull marriedgorillas/gnuradio-non-root
    ```
3.  **Run Container**:
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
    *(Note check `xhost` commands in legacy notes if GUI doesn't appear)*

## 🚦 Usage

1.  **Start the Channel simulation**:
    Open `simulationChannel/pkt_xmt.grc` (and `pkt_rcv` if separate) in GNU Radio Companion and run them.
    *Alternatively, run the generated python scripts directly.*

2.  **Start the Receiver**:
    ```bash
    python3 fileSubscriber.py --port 5555 --file_directory ./receiver_side_files
    ```

3.  **Start the Sender**:
    ```bash
    python3 filePublisher.py --port 5555 --file_directory ./sender_side_files
    ```
    The sender will automatically detect files in the folder and begin transmission.

## 🔮 Future Work & Concepts

The original vision for this project was to implement a **Semantic Autoencoder**:
- **Encoder**: Use **BLIP-2** to generate dense semantic captions of images, followed by text embedding.
- **Decoder**: Use **Segment Anything** or Stable Diffusion to reconstruct the image from the received semantic tokens.
This infrastructure was designed to carry those semantic tokens instead of raw file bytes, enabling extreme compression for specific tasks.

## ⚠️ Known Limitations
- **Platform**: Native macOS support for GNU Radio is experimental.
- **Protocol**: The custom framing protocol currently uses fixed padding which may result in overhead.
- **Flow Control**: Relies partially on basic sleep timers; production use should implement robust ARQ.
