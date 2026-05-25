#!/bin/sh
set -eu

seed_dir() {
  src="$1"
  dest="$2"

  mkdir -p "$dest"
  if [ -z "$(ls -A "$dest" 2>/dev/null)" ]; then
    cp -a "$src"/. "$dest"/
  fi
}

seed_dir /opt/bemsrlstudio-seed/buildings /workspaces/sinergym/sinergym/data/buildings
seed_dir /opt/bemsrlstudio-seed/weather /workspaces/sinergym/sinergym/data/weather
seed_dir /opt/bemsrlstudio-seed/default_configuration /workspaces/sinergym/sinergym/data/default_configuration

mkdir -p /workspaces/sinergym/Sinergym-logs
mkdir -p /workspaces/sinergym/models

exec "$@"
