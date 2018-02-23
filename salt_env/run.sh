#!/bin/bash



docker pull ubuntu:16.04
git clone https://github.com/Mirantis/mcp-common-scripts.git scripts
docker run -v $(pwd)/:/tests -u root:root --hostname=apt01 --ulimit nofile=4096:8192 --cpus=2 --rm -it  ubuntu:16.04 /bin/bash cd /tests/scripts/mirror-image/
