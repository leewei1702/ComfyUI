# ComfyUI for CUDA and CPU

## Prerequisite 
1. Install [Docker](https://www.docker.com/get-started/)
<br>

## Guideline for building and pushing your own ComfyUI images

1. Run the command below to build your image with the correspondiing hardware, replace <image_name> with your own image name
    - Nvidia GPU
        ```
        docker build -t <image_name> -f Dockerfile.cuda .
        ```
    - CPU Only
        ```
        docker build -t <image_name> -f Dockerfile.cpu .
        ```

2. Run the command below to push it to remote repository, replace <image_name> with your own image name
```
docker push <image_name>
```
<br>

## My own CUDA and CPU images 
[Link to my ComfyUI images](https://hub.docker.com/r/leewei1702/comfyui)
</br>

## Run one of the command below to pull my ComfyUI images
### CUDA 12.8
```
docker pull leewei1702/comfyui:cuda
```
### CPU
```
docker pull leewei1702/comfyui:cpu
```
<br>

