#!/bin/bash

set -e

image_tag="capstone-runner:latest"

build_path="$(dirname $0)"

# Check if an image with the same tag exists
old_image_id=$(docker images -q "$image_tag")

# Build the new Docker image
echo "Building new Docker image with tag: $image_tag"
docker build -t "$image_tag" "$build_path"

# Delete previous version of image if it's not the same as new image
image_id=$(docker images -q "$image_tag")
if [ -z "$old_image_id" ]; then
    echo "Previous version of image was not found"
elif [ "$old_image_id" = "$image_id" ]; then
    echo "Previous version of image is same as new version"
else
    echo "Deleting previous image with id: $old_image_id"
    docker rmi -f "$old_image_id"
fi
