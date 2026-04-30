#!/bin/bash
cd /root/.openclaw/workspace/prompt-studio-api
pkill -f "server.py" 2>/dev/null
sleep 1
nohup /root/.openclaw/workspace/prompt-studio-api/venv/bin/python server.py > server.log 2>&1 &
echo "Server started, PID: $!"
sleep 2
curl -s http://localhost:5001/api/stats
