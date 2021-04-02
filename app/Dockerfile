FROM gcr.io/gem5-test/ubuntu-20.04_all-dependencies AS gem5_builder

WORKDIR /opt

RUN git clone https://github.com/devplayer0/gem5
RUN cd gem5 && scons build/ARM/gem5.fast -j$(nproc)


FROM ubuntu:20.04
ARG PYOCD_TARGET=stm32f407
ARG LIBOPENCM3_TAG=0d72e6739c5f7c90f28350a8bb228722ff094806

# gem5 runtime dependencies
RUN apt-get update && \
    apt-get install -y python3 libpython3.8 libprotobuf17 libhdf5-cpp-103 libpng16-16

# Only the necessary gem5 bits
RUN mkdir -p /opt/gem5/build/ARM
COPY --from=gem5_builder /opt/gem5/build/ARM/gem5.fast /opt/gem5/build/ARM/gem5.fast
RUN mkdir -p /opt/gem5/build/ARM/perfgrade/proto
COPY --from=gem5_builder /opt/gem5/build/ARM/perfgrade/proto/ /opt/gem5/build/ARM/perfgrade/proto/

WORKDIR /opt
COPY requirements.txt setup.py /opt/perfgrade/
RUN apt-get install -y python3-setuptools python3-pip && \
    cd perfgrade && \
    pip3 install -r requirements.txt

RUN apt-get install -y git build-essential binutils-arm-none-eabi gcc-arm-none-eabi
RUN git clone https://github.com/libopencm3/libopencm3 && \
    cd libopencm3 && \
    git checkout 0d72e6739c5f7c90f28350a8bb228722ff094806 && \
    make -j$(nproc)

RUN apt-get install -y libusb-1.0-0 && \
    pyocd pack -i "$PYOCD_TARGET"

COPY perfgrade/ /opt/perfgrade/perfgrade/
RUN cd perfgrade && \
    pip3 install . && \
    rm -r /opt/perfgrade

ENTRYPOINT ["perfgrade"]
