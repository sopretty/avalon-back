#!/bin/bash
docker build --no-cache -t avalon-pkg .
docker-compose up -d
docker logs -f avalon-back_api_1
