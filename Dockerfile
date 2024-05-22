FROM continuumio/miniconda3

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY environment.yml .
RUN conda env create -f environment.yml

RUN echo "source activate myenv" > ~/.bashrc
ENV PATH /opt/conda/envs/myenv/bin:$PATH

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN conda install -c conda-forge ncbi-datasets-cli