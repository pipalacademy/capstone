#!/bin/bash

set -e

image_tag="capstone-runner:latest"

build_path="$(dirname $0)"

# Check if an image with the same tag exists
image_id=$(docker images -q "$image_tag")

# Build the new Docker image
echo "Building new Docker image with tag: $image_tag"
docker build -t "$image_tag" "$build_path"

# If an old version of the image exists, delete it
if [ -n "$image_id" ]; then
    echo "Deleting previous image with tag: $image_tag"
    docker rmi -f "$image_id"
fi
