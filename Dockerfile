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
COPY . /app

# Install required Python packages.
RUN pip3 install --no-cache-dir paho-mqtt cbor2 schedule time

# Create the directories for mosquitto configuration and certificates.
RUN mkdir -p /etc/mosquitto/conf.d && mkdir -p /etc/mosquitto/certs

# Copy the provided Mosquitto configuration file to the expected location.
RUN cp /app/CSMIM_Network/Broker_Config/mosquitto.conf /etc/mosquitto/mosquitto.conf

# ---------------------------------------------------------------
# Certificate Generation Automation:
# This script automatically creates:
#   - A fake CA key, CSR, and root certificate.
#   - The server key, CSR, and a server certificate signed by the fake CA.
#
# The certificates are stored in /etc/mosquitto/certs.
# ---------------------------------------------------------------
RUN mkdir -p /app/scripts
RUN echo '#!/bin/bash' > /app/scripts/gen_certs.sh && \
    echo 'set -e' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo '# Configuration variables' >> /app/scripts/gen_certs.sh && \
    echo 'CERT_DIR="/etc/mosquitto/certs"' >> /app/scripts/gen_certs.sh && \
    echo 'CA_PASS="secret"  # For demo purposes only; use secure methods in production' >> /app/scripts/gen_certs.sh && \
    echo 'SERVER_CN="localhost"  # Change if your broker hostname is different' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo '# Ensure the certificate directory exists' >> /app/scripts/gen_certs.sh && \
    echo 'mkdir -p "$CERT_DIR"' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Generating the fake CA key..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl genrsa -des3 -passout pass:"$CA_PASS" -out "$CERT_DIR/ca.key" 2048' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Generating the fake CA certificate signing request..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl req -new -key "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -subj "/C=US/ST=Arizona/L=Embry/O=Fake Authority/CN=Fake-CA" -out "$CERT_DIR/ca-cert-request.csr" -sha256' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Creating the fake CA root certificate..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl x509 -req -in "$CERT_DIR/ca-cert-request.csr" -signkey "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -out "$CERT_DIR/ca-root-cert.crt" -days 365 -sha256' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Generating the server key..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl genrsa -out "$CERT_DIR/server.key" 2048' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Generating the server certificate signing request..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl req -new -key "$CERT_DIR/server.key" -subj "/C=US/ST=Arizona/L=Embry/O=CSMIM Team/CN=${SERVER_CN}" -out "$CERT_DIR/server-cert-request.csr" -sha256' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Signing the server certificate using the fake CA..."' >> /app/scripts/gen_certs.sh && \
    echo 'openssl x509 -req -in "$CERT_DIR/server-cert-request.csr" -CA "$CERT_DIR/ca-root-cert.crt" -CAkey "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -CAcreateserial -out "$CERT_DIR/server.crt" -days 360 -sha256' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "==> Setting file permissions on certificate files..."' >> /app/scripts/gen_certs.sh && \
    echo 'chmod 644 "$CERT_DIR/ca.key" "$CERT_DIR/ca-cert-request.csr" "$CERT_DIR/ca-root-cert.crt" "$CERT_DIR/server.key" "$CERT_DIR/server-cert-request.csr" "$CERT_DIR/server.crt"' >> /app/scripts/gen_certs.sh && \
    echo '' >> /app/scripts/gen_certs.sh && \
    echo 'echo "Certificates have been generated in $CERT_DIR"' >> /app/scripts/gen_certs.sh

# Make the certificate generation script executable and run it.
RUN chmod +x /app/scripts/gen_certs.sh && /app/scripts/gen_certs.sh

# Expose the Mosquitto TLS port (8883) if the container is run as a broker.
EXPOSE 8883

# open command prompt
CMD ["/bin/bash"]
