#!/bin/bash

# Run from inside of the project directory

# Load environment variables from dotenv file
. ./.env

aws_id="${AWS_ACCOUNT_ID}"
region="${AWS_REGION_NAME}"
image="${IMAGE_NAME}"
version="${VERSION_TAG}"

ecr_url="${aws_id}.dkr.ecr.${region}.amazonaws.com"

source_image_tag="${image}:${version}"

target_ecr_tag="${ecr_url}/${source_image_tag}"

echo "$target_ecr_tag"


# login to ecr docker registry
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin "${ecr_url}"

# pull ats-backend docker image
docker pull "${target_ecr_tag}"

# Tag the image for ECR
echo "Tagging back from '${target_ecr_tag}' to '${source_image_tag}'"
docker tag "${target_ecr_tag}" "${source_image_tag}"

# run pulled image of ATS
if [ -x "$(command -v docker-compose)" ]; then
  docker-compose --env-file .env up -d pgdb
  docker-compose --env-file .env up -d --no-build server
  docker-compose run --rm server alembic upgrade head
else
  docker compose --env-file .env up -d pgdb
  docker compose --env-file .env up -d --no-build server
  docker compose run --rm server alembic upgrade head
fi
