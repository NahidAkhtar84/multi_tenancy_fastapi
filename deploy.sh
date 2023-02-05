#!/bin/bash

# Run from inside of the project directory

if [ $# -lt 1 ]; then
  echo "Argument missing"; exit 1; fi
if [ ${1} != 'dev' ] && [ ${1} != 'prod' ] && [ ${1} != 'dev_new' ]; then
  echo "invalid arg-1. Use 'dev' / 'prod' / 'dev_new'"; exit 1; fi
if [ $# -eq 2 ] && [ ${2} != 'build' ] && [ ${2} != 'up' ];  then
  echo "invalid arg-2. Use 'build', 'up' or skip the arg-2"; exit 1; fi

deploy_env=${1}
ENV_FILE="${deploy_env}.env"

# Find git HEAD commit hash and replace the VERSION_COMMIT_HASH value in env file
commit_hash=$(git rev-parse --short HEAD)
sed -i -r "s#^(VERSION_COMMIT_HASH=).*#\1$commit_hash#" ${ENV_FILE}

# Load environment variables from dotenv file
. "./${ENV_FILE}"

aws_id="${AWS_ACCOUNT_ID}"
region="${AWS_REGION_NAME}"
image="${IMAGE_NAME}"
version="${VERSION_TAG}"

profile="${AWS_PROFILE_NAME}"
key_pair="${KEY_PAIR_FILE}"
_deploy_host="${DEPLOY_HOST}"
_deploy_path="${DEPLOY_PATH}"

if [ $# -eq 1 ] || [ ${2} = 'build' ];  then

  # Copy deployment files to deploy_location
  scp -i ${key_pair} ${ENV_FILE} "${_deploy_host}:${_deploy_path}/.env"
  scp -i ${key_pair} "docker-compose.yaml" "${_deploy_host}:${_deploy_path}/docker-compose.yaml"
  scp -i ${key_pair} "script-pull-and-run.sh" "${_deploy_host}:${_deploy_path}/script-pull-and-run.sh"

  # Create ECR compatible tag name
  ecr_url="${aws_id}.dkr.ecr.${region}.amazonaws.com"
  source_image_tag="${image}:${version}"
  target_ecr_tag="${ecr_url}/${source_image_tag}"

  # Build docker image
  echo "\nDocker image building..."
  if [ -x "$(command -v docker-compose)" ]; then
    docker-compose --env-file "${ENV_FILE}" build
  else
    docker compose --env-file "${ENV_FILE}" build
  fi
  echo "\nDocker image build done"

  # Tag the image for ECR
  echo "\nTagging '${source_image_tag}' to '${target_ecr_tag}'"
  docker tag "${source_image_tag}" "${target_ecr_tag}"

  # ecr docker login
  aws ecr get-login-password --profile ${profile} --region ${region} | docker login --username AWS --password-stdin "${ecr_url}"

  # PUSH to ECR
  echo "\nPushing the docker image to ECR"
  docker push "${target_ecr_tag}"
fi

if [ $# -eq 1 ] || [ ${2} = 'up' ];  then
  # ssh to remote machine and run script-pull-and-run.sh to deploy
  ssh -i "${key_pair}" "${_deploy_host}" "cd ${image}; sh script-pull-and-run.sh"
fi

