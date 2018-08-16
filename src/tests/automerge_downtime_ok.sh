#!/bin/bash
set -e

usage () {
  echo "Usage: $(basename "$0") BASE_SHA MERGE_COMMIT_SHA"
  exit 1
}

fail () {
  echo "$@" >&2
  exit 1
}

zread () {
  # read a NUL-terminated token
  IFS='' read -r -d '' "$@"
}

[[ $1 =~ ^[0-9a-f]{40}$ ]] || usage
[[ $2 =~ ^[0-9a-f]{40}$ ]] || usage
BASE_SHA=$1
MERGE_COMMIT_SHA=$2

#cd "$(git rev-parse --show-toplevel)"

git merge-base --is-ancestor "$BASE_SHA" "$MERGE_COMMIT_SHA" ||
fail "BASE_SHA ($BASE_SHA) is not an ancestor commit of" \
     "MERGE_COMMIT_SHA ($MERGE_COMMIT_SHA)"

DTs=()
E=()
while zread NAME; do
  if [[ $NAME =~ ^topology/[^/]+/[^/]+/[^/]+_downtime.yaml$ ]]; then
    DTs+=("$NAME")
  else
    E+=("File '$NAME' is not a downtime file.")
  fi
done < <(git diff -z --name-only "$BASE_SHA" "$MERGE_COMMIT_SHA")

if [[ $E ]]; then
  echo "Commit is not eligible for auto-merge:"
  for e in "${E[@]}"; do
    echo "$e"
  done
  exit 1
else
  echo "Commit is eligible for auto-merge."
  exit 0
fi

