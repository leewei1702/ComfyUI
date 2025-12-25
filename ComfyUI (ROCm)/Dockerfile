FROM rocm/pytorch:rocm6.4.2_ubuntu24.04_py3.12_pytorch_release_2.6.0

WORKDIR /ComfyUI

RUN apt-get update && apt-get install -y \
  git \
  wget \
  python3 \
  python3-pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

COPY requirements_rocm.txt .

RUN pip3 install --no-cache-dir -r requirements_rocm.txt

RUN pip3 install --no-cache-dir comfy-cli

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager ./custom_nodes/comfyui-manager

RUN pip3 install --no-cache-dir -r ./custom_nodes/comfyui-manager/requirements.txt

RUN yes | comfy model download --url https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors --filename stable-diffusion-v1-5-pruned.safetensors --relative-path models/checkpoints

# Preinstall workflow
COPY ./ComfyUI_Workflow/*.json /ComfyUI/user/default/workflows/

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8188

CMD ["/start.sh"]

