#!/bin/bash

comfy launch -- --listen 0.0.0.0 &

bash /app/backend/start.sh
