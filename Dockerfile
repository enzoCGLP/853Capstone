# Use Ubuntu 20.04 as the base image.
FROM ubuntu:20.04

# Disable interactive prompts during package installation.
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:mosquitto-dev/mosquitto-ppa && \
    apt-get update && \
    apt-get install -y \
      mosquitto \
      mosquitto-clients \
      openssl \
      python3 \
      python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy repo to container
COPY ./CSMIM_Network /app

# Install required Python packages.
RUN pip3 install --no-cache-dir paho-mqtt cbor2 schedule

# Create the directories for mosquitto configuration and certificates.
RUN mkdir -p /etc/mosquitto/conf.d && mkdir -p /etc/mosquitto/certs

# Copy the provided Mosquitto configuration file to the expected location.
RUN cp /app/CSMIM_Network/Broker_Config/mosquitto.conf /etc/mosquitto/mosquitto.conf

# Expose the Mosquitto TLS port (8883) if the container is run as a broker.
EXPOSE 8883

# open command prompt
CMD ["/bin/bash"]
