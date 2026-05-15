FROM public.ecr.aws/debian/debian:bookworm

ARG TARGETPLATFORM
ARG SAMTOOLS_VERSION="1.22.1"
ARG WRAPICA_VERSION="2.45.0"
ARG PYTHON_VERSION="3.14"

RUN \
    if [ "${TARGETPLATFORM#linux/}" = "arm64" ]; then \
      platform_url="aarch64";  \
    else \
      platform_url="x86_64"; \
    fi && \
    echo "Standard APT" 1>&2 && \
    apt update -yq && \
    apt upgrade -yq && \
    # Basics along with htslib/samtools deps \
    apt install -yq \
      build-essential \
      libz-dev \
      wget \
      curl \
      pigz \
      unzip \
      jq \
      python3 \
      git \
      zlib1g-dev \
      libbz2-dev \
      liblzma-dev \
      xz-utils \
      libssl-dev \
      libncurses5-dev \
      libcurl4-openssl-dev \
      liblzma-dev \
      procps \
      libopenblas-dev \
      libgomp1 && \
    # Download + Install samtools \
    wget \
      --quiet \
      --output-document "samtools-${SAMTOOLS_VERSION}.tar.bz2" \
      "https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2" && \
    tar -xf "samtools-${SAMTOOLS_VERSION}.tar.bz2" && \
    ( \
      cd "samtools-${SAMTOOLS_VERSION}" && \
      ./configure \
        --enable-plugins \
        --prefix=/usr && \
      make all all-htslib && \
      make install install-htslib \
    ) && \
    rm -rf \
      "samtools-${SAMTOOLS_VERSION}" \
      "samtools-${SAMTOOLS_VERSION}.tar.bz2" && \
    # Install AWS \
    wget \
      --quiet \
      --output-document "awscliv2.zip" \
      "https://awscli.amazonaws.com/awscli-exe-linux-${platform_url}.zip" && \
    unzip -q "awscliv2.zip" && \
    ./aws/install \
      --install-dir /usr/aws-cli \
      --bin-dir /usr/bin && \
    rm -rf "awscliv2.zip" "aws/" && \
    # Install UV \
    echo "Installing UV" 1>&2 && \
    curl -LsSf https://astral.sh/uv/install.sh | \
    XDG_CONFIG_HOME=/tmp UV_INSTALL_DIR=/usr/bin sh && \
    echo "Installing Python packages via uv" 1>&2 && \
    echo "Install wrapica" 1>&2 && \
    uv venv \
      --python "${PYTHON_VERSION}" && \
    uv pip install \
      wrapica=="${WRAPICA_VERSION}"

# Copy the docker entrypoint to the docker container
COPY docker-entrypoint.sh docker-entrypoint.sh

# Install the scripts
COPY scripts/ scripts/

# Make the docker entrypoint executable
RUN chmod +x "./docker-entrypoint.sh"

# Set the entrypoint as the docker entrypoint script
CMD [ "./docker-entrypoint.sh" ]
