FROM hyperledger/indy-core-baseci:0.0.1
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

ARG uid=1000
ARG user=indy
ARG venv=venv

RUN echo "deb https://repo.sovrin.org/test/deb xenial rocksdb" >> /etc/apt/sources.list && \
    apt-get update

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.2.0 \
    libindy=1.3.1~403 \
    librocksdb=5.8.8

RUN indy_ci_add_user $uid $user $venv

RUN indy_image_clean

USER $user
WORKDIR /home/$user
