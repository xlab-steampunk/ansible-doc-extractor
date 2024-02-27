#!/bin/bash

set -euo pipefail

export ANSIBLE_COLLECTIONS_PATH=$(pwd)
ansible-doc-extractor . ./ansible_collections/sensu/sensu_go/plugins/modules/*.py
