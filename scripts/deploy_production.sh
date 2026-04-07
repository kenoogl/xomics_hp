#!/usr/bin/env bash
set -euo pipefail

: "${DEPLOY_HOST:?DEPLOY_HOST is required}"
: "${DEPLOY_USER:?DEPLOY_USER is required}"

DEPLOY_PORT="${DEPLOY_PORT:-22}"
TARGET_DIR="${PRODUCTION_TARGET_DIR:-/var/www/html}"
SSH_OPTS="-p ${DEPLOY_PORT} -o StrictHostKeyChecking=no"

rsync -az --delete -e "ssh ${SSH_OPTS}" public/ "${DEPLOY_USER}@${DEPLOY_HOST}:${TARGET_DIR}/"
ssh ${SSH_OPTS} "${DEPLOY_USER}@${DEPLOY_HOST}" "sudo apache2ctl configtest && sudo systemctl reload apache2"
