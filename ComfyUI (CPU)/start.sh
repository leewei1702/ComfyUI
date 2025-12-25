#!/bin/bash

comfy launch -- --cpu --listen 0.0.0.0 &

bash /app/backend/start.sh
