#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Installing Python dependencies..."

python3 -m pip install --upgrade pip

python3 -m pip install "cython==0.29.37"
python3 -m pip install "pyyaml==6.0.2"
python3 -m pip install "argparse==1.4.0"
python3 -m pip install "onnxruntime==1.19.0"
python3 -m pip install "tqdm==4.66.5"
python3 -m pip install "nemo_toolkit @ git+https://github.com/AI4Bharat/NeMo@nemo-v2"
python3 -m pip install "transformers==4.40.0"
python3 -m pip install "huggingface_hub==0.23"
python3 -m pip install "pytorch-lightning==2.4.0"
python3 -m pip install "hydra-core==1.3.2"
python3 -m pip install "librosa==0.10.2.post1"
python3 -m pip install "sentencepiece==0.2.0"
python3 -m pip install "pandas==2.2.2"
python3 -m pip install "lhotse==1.27.0"
python3 -m pip install "editdistance==0.8.1"
python3 -m pip install "jiwer==3.0.4"
python3 -m pip install "pyannote.audio==3.3.1"
python3 -m pip install "webdataset==0.2.100"
python3 -m pip install "datasets==2.21.0"
python3 -m pip install "IPython==8.27.0"
python3 -m pip install "joblib==1.4.2"

echo "All packages installed successfully."
