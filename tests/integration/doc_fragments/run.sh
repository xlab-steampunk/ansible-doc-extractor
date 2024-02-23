#!/bin/bash

set -euo pipefail

ansible-doc-extractor . ./ansible_collections/sensu/sensu_go/plugins/modules/*.py
