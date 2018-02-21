FROM hyperledger/indy-core-baseci:0.0.1
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

ARG uid=1000
ARG user=indy
ARG venv=venv

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.2.0 \
    libindy=1.3.1~402

RUN indy_ci_add_user $uid $user $venv

RUN indy_image_clean

USER $user
WORKDIR /home/$user
