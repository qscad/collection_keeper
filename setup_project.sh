#!/bin/sh

set -e

git init .
git add -A .
git commit -m "feat: init a repo"

pdm install
