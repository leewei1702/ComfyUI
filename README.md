# ComfyUI
</br>

## Prerequisite 
Install [Docker](https://www.docker.com/get-started/)

## Guideline for building and pushing your own ComfyUI images
Run the command below to build it, replace <image_name> with your own image name
```
docker build -t <image_name> .
```
Run the command below to push it to remote repository, replace <image_name> with your own image name
```
docker push <image_name>
```
