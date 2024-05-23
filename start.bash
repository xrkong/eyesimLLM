#!/bin/bash
#export EYESIM_MAP='worlds/aquatic/mountain.wld'
docker compose up -d
docker exec -u 0 eyesim sed -i '/world/c\world '${EYESIM_MAP} /opt/eyesim/eyesimX/default.sim 
docker exec eyesim eyesim
# if [ -n "$EYESIM_MAP" ]; then
#     sed -i '/world/c\world '${EYESIM_MAP} /opt/eyesim/eyesimX/default.sim 
# fi