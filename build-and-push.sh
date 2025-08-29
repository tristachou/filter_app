#!/bin/bash

# 停止前一個指令失敗時繼續執行
set -e

docker buildx build --platform linux/amd64 -t 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-backend:latest ./backend --push
echo "finish pushing backend image！"
echo ""


docker buildx build --platform linux/amd64 -t 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-frontend:latest ./frontend --push
echo "finish pushing frontend image！"
echo ""

docker buildx build --platform linux/amd64 -t 901444280953.dkr.ecr.ap-southeast-2.amazonaws.com/filter-app-nginx:latest ./nginx --push
echo "finish pushing Nginx image！"
echo ""

