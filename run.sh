#!/usr/bin/env bash
cd /home/ainur/robot_delivery/robot_delivery_system
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 >> backend.log 2>&1 &