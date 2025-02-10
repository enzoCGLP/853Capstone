# Use Ubuntu as base image
FROM ubuntu:20.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install requirements
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:mosquitto-dev/mosquitto-ppa && \
    apt-get update && \
    apt-get install -y \
      mosquitto \
      mosquitto-clients \
      python3 \
      python3-pip \
      openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the entire repository into 
COPY . /app

# Install libs
RUN pip3 install --no-cache-dir paho-mqtt cbor2 schedule time

# -----------------------------------------------------------
# Certificate and Mosquitto Configuration Automation Script
# -----------------------------------------------------------
# We will create a shell script that:
#   1. Generates the fake CA key, CSR, and root certificate.
#   2. Generates the server key, CSR, and signs the server certificate.
#   3. Sets file permissions.
#   4. Writes the mosquitto.conf file using your provided configuration.
#
# The generated certificates will be placed in /etc/mosquitto/certs
# and the configuration file at /etc/mosquitto/mosquitto.conf.
# -----------------------------------------------------------

# Create a directory for the script.
RUN mkdir -p /app/scripts

# Write the automation script.
RUN echo '#!/bin/bash' > /app/scripts/setup_certs_and_config.sh && \
    echo 'set -e' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# Define variables' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'CERT_DIR="/etc/mosquitto/certs"' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'MOSQUITTO_CONF="/etc/mosquitto/mosquitto.conf"' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'CA_PASS="secret"  # For demo only; use env variables in production' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'SERVER_CN="localhost"  # Change if your broker hostname differs' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# Ensure the certificate directory exists' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'mkdir -p "$CERT_DIR"' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Generating the fake CA key..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl genrsa -des3 -passout pass:"$CA_PASS" -out "$CERT_DIR/ca.key" 2048' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Generating the fake CA certificate signing request..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl req -new -key "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -subj "/C=US/ST=Arizona/L=Embry/O=Fake Authority/CN=Fake-CA" -out "$CERT_DIR/ca-cert-request.csr" -sha256' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Creating the fake CA root certificate..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl x509 -req -in "$CERT_DIR/ca-cert-request.csr" -signkey "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -out "$CERT_DIR/ca-root-cert.crt" -days 365 -sha256' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Generating the server key..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl genrsa -out "$CERT_DIR/server.key" 2048' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Generating the server certificate signing request..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl req -new -key "$CERT_DIR/server.key" -subj "/C=US/ST=Arizona/L=Embry/O=CSMIM Team/CN=${SERVER_CN}" -out "$CERT_DIR/server-cert-request.csr" -sha256' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Signing the server certificate using the fake CA..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'openssl x509 -req -in "$CERT_DIR/server-cert-request.csr" -CA "$CERT_DIR/ca-root-cert.crt" -CAkey "$CERT_DIR/ca.key" -passin pass:"$CA_PASS" -CAcreateserial -out "$CERT_DIR/server.crt" -days 360 -sha256' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Setting file permissions on certificates..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'chmod 644 "$CERT_DIR/ca.key" "$CERT_DIR/ca-cert-request.csr" "$CERT_DIR/ca-root-cert.crt" "$CERT_DIR/server.key" "$CERT_DIR/server-cert-request.csr" "$CERT_DIR/server.crt"' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "Certificates generated in $CERT_DIR"' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "==> Generating mosquitto.conf file..."' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'cat > "$MOSQUITTO_CONF" <<EOF' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# Place your local configuration in /etc/mosquitto/conf.d/' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# A full description of the configuration file is at' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# /usr/share/doc/mosquitto/examples/mosquitto.conf.example' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '#pid_file /run/mosquitto/mosquitto.pid' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'persistence true' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'persistence_location /var/lib/mosquitto/' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'log_dest file /var/log/mosquitto/mosquitto.log' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'per_listener_settings false' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'include_dir /etc/mosquitto/conf.d' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# Secure TLS port' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'listener 8883' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'allow_anonymous false' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'password_file /etc/mosquitto/passwordfile' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# Certificates' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'cafile /etc/mosquitto/certs/ca-root-cert.crt' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'keyfile /etc/mosquitto/certs/server.key' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'certfile /etc/mosquitto/certs/server.crt' >> /app/scripts/setup_certs_and_config.sh && \
    echo '' >> /app/scripts/setup_certs_and_config.sh && \
    echo '# TLS version' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'tls_version tlsv1.3' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'EOF' >> /app/scripts/setup_certs_and_config.sh && \
    echo 'echo "Mosquitto configuration generated at $MOSQUITTO_CONF"' >> /app/scripts/setup_certs_and_config.sh

# Make the script executable.
RUN chmod +x /app/scripts/setup_certs_and_config.sh

# Run the certificate and configuration generation script.
RUN /app/scripts/setup_certs_and_config.sh

# Expose the TLS port 
EXPOSE 8883

# opens shell on execution
CMD ["/bin/bash"]
