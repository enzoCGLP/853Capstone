# Use Ubuntu 20.04 as the base image.
FROM ubuntu:20.04

# Disable interactive prompts during package installation.
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update && \
    apt-get install -y \
      mosquitto \
      mosquitto-clients \
      openssl \
      python3 \
      python3-pip \
      #network utilities for testing:
      iproute2 \
      iputils-ping && \
      #end network utilites list
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy repo to container
COPY . /app

# Install required Python packages.
RUN pip3 install --no-cache-dir paho-mqtt cbor2 schedule

# Create the directories for mosquitto configuration and certificates.
RUN mkdir -p /etc/mosquitto/conf.d && mkdir -p /etc/mosquitto/certs

# Copy the provided Mosquitto configuration file to the expected location.
RUN cp ./CSMIM_Network/CDS_Config/mosquitto.conf /etc/mosquitto/mosquitto.conf

# Copy the provided certification files and password file to the expected location.
RUN cp ./CSMIM_Network/Client_v_1_6_raw/certs/ca-root-cert.crt /etc/mosquitto/certs/ca-root-cert.crt
RUN cp ./CSMIM_Network/Client_v_1_6_raw/certs/server.crt /etc/mosquitto/certs/server.crt
RUN cp ./CSMIM_Network/Client_v_1_6_raw/certs/server.key /etc/mosquitto/certs/server.key
RUN cp ./CSMIM_Network/Client_v_1_6_raw/certs/ca.key /etc/mosquitto/certs/ca.key
RUN cp ./CSMIM_Network/CDS_Config/passwordfile /etc/mosquitto/passwordfile

# Update permissions for certification files
RUN chmod 644 /etc/mosquitto/certs/ca.key && chmod 644 /etc/mosquitto/certs/server.key

# Expose the Mosquitto TLS port (8883) if the container is run as a broker.
EXPOSE 8883

# open command prompt
CMD ["/bin/bash"]
