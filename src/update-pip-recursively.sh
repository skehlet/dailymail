#!/bin/bash
set -e

# `brew install gnu-sed`

MY_DIR=$(dirname $0)
cd "$MY_DIR"

for dir in *
do
    if [[ -f $dir/requirements.txt ]]; then
        echo $dir
        cd $dir
        gsed -i -e 's/==.*//' requirements.txt
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        pip freeze > requirements.txt
        deactivate
        rm -rf .venv
        cd ..
    fi
done
