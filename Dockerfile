#FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04
#FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04
#FROM  nvidia/cuda:12.6.3-devel-ubuntu22.04
# FROM nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime
#FROM pytorch/pytorch:1.7.1-cuda11.0-cudnn8-runtime

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Add Deadsnakes PPA and install Python 3.12
#RUN apt-get update && \
#    apt-get install -y software-properties-common && \
#    add-apt-repository ppa:deadsnakes/ppa && \
#    apt-get update && \
#    apt-get install -y python3.12 python3.12-venv && \
#    apt-get install -y curl && \
#    rm -rf /var/lib/apt/lists/*

# Create symbolic links for python and pip
RUN ln -s /usr/bin/python3.12 /usr/bin/python

#RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
#    python3.12 get-pip.py

#RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
#    update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.12 1
#RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

# Copy the source code into the container.
COPY ./llmpackagequery /app

RUN pip install --user -r requirements.txt
#RUN pip install -I six

#RUN apt update && apt install libstdc++6 libstdc++6

# Run main
# CMD ["python3", "main.py"]

# override standard entrypoint and run the application
# ENTRYPOINT ["python3", "main.py"]
ENTRYPOINT ["python3", "query_llm"]
