#!/bin/bash
docker build -t avalon-pkg .
docker-compose up -d
#docker logs -f avalonapp_api_1
