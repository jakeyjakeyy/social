#!/bin/bash

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color


# Step 0: Checklist
echo -e "${YELLOW}Step 0: Checklist...${NC}"
read -p "Did you update your .envs? (y/n)" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${RED}Update your .envs before deploying.${NC}"
    exit 1
fi
read -p "Did you update your Dockerfiles? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${RED}Update your Dockerfiles before deploying.${NC}"
    exit 1
fi

# Parse arguments
NO_BUILD=false
NO_DEPLOY=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-build) NO_BUILD=true ;;
        --no-deploy) NO_DEPLOY=true ;;
        *) echo -e "${RED}Unknown parameter passed: $1${NC}"; exit 1 ;;
    esac
    shift
done

# Step 1: Build docker images
if [ "$NO_BUILD" = false ]; then
    echo -e "${YELLOW}Step 1: Building docker images...${NC}"
    docker rmi $(docker images -q)
    docker compose build --no-cache
else
    echo -e "${YELLOW}Skipping Step 1: Build docker images (--no-build flag provided).${NC}"
fi

# Step 2: Tag frontend and backend images
if [ "$NO_BUILD" = false ]; then
    echo -e "${YELLOW}Step 2: Tagging frontend and backend images...${NC}"
    docker tag "social-frontend:latest" "docker.io/jakerichards/social_frontend"
    docker tag "social-backend:latest" "docker.io/jakerichards/social_backend"
else
    echo -e "${YELLOW}Skipping Step 2: Tagging images (--no-build flag provided).${NC}"
fi

# Step 3: Push frontend/backend images
if [ "$NO_BUILD" = false ]; then
    echo -e "${YELLOW}Step 3: Pushing frontend/backend images...${NC}"
    docker push "docker.io/jakerichards/social_frontend"
    docker push "docker.io/jakerichards/social_backend"
else
    echo -e "${YELLOW}Skipping Step 3: Pushing images (--no-build flag provided).${NC}"
fi

# Step 4: SSH into server
if [ "$NO_DEPLOY" = false ]; then
    echo -e "${YELLOW}Step 4: SSH into server...${NC}"
    ssh jakerichards <<EOF
        # Step 5: Stop old docker images
        echo -e "${YELLOW}Step 5: Stopping old docker images...${NC}"
        cd "social"
        docker-compose down

        # Step 6: Remove old images
        echo -e "${YELLOW}Step 6: Removing old images...${NC}"
        docker rmi \$(docker images -q)

        # Step 7: Update local files
        echo -e "${YELLOW}Step 7: Updating local files...${NC}"
        git stash
        git pull
        git stash pop

        # Step 8: Deploy
        echo -e "${YELLOW}Step 8: Deploying...${NC}"
        docker-compose up -d
EOF
else
    echo -e "${YELLOW}Skipping Steps 4-8: Deployment (--no-deploy flag provided).${NC}"
fi

echo -e "${GREEN}Deployment completed successfully.${NC}"