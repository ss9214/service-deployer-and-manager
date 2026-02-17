FROM hashicorp/terraform:1.7

# Install additional tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    bash \
    git \
    openssh \
    jq

# Install AWS CLI
RUN pip3 install --no-cache-dir awscli boto3

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Python dependencies for setup script
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy setup script
COPY setup.py /app/setup.py
COPY templates/ /app/templates/

WORKDIR /app

# Set entrypoint
ENTRYPOINT ["python3", "setup.py"]
