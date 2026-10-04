#!/bin/bash

# This script manages the lifecycle of a Docker container named "ultimate-max-planner-api".
# It provides functions to start the container in either detached or interactive mode,
# stop the container, and restart the container. The script accepts command-line arguments
# to determine the action to perform.

# Usage:
#   ./server_docker.sh [option]
#
# Options:
#   -it   Start the container in interactive mode.
#   -s    Stop the container if it is running.
#   -r    Restart the container.
#   (no option) Start the container in detached mode.
#
# The container is configured to map port 5200 on the host to port 5200 in the container.
# It also mounts the following directories and files from the host to the container:
#   - $(pwd)/Server to /app/Server
#   - $(pwd)/Dictionary to /app/Dictionary
#   - $(pwd)/requirements.txt to /app/requirements.txt
#
# The container image used is "kaboom-server:1.1".
#!/bin/bash

CONTAINER_NAME="ultimate-max-planner-api"

start_detached() {
    sudo docker run -d --rm --name $CONTAINER_NAME -p 5200:5200 ultimate-max-planner-api:latest
}

start_interactive() {
    sudo docker run -it --rm --name $CONTAINER_NAME -p 5200:5200 ultimate-max-planner-api:latest
}

stop_container() {
    sudo docker stop $CONTAINER_NAME
}

restart_container() {
    stop_container
    start_detached
}

case "$1" in
    -it)
        start_interactive
        ;;
    -s)
        stop_container
        ;;
    -r)
        restart_container
        ;;
    *)
        start_detached
        ;;
esac