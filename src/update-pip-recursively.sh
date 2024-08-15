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
        cp -p requirements.txt requirements.orig.txt
        gsed -i -e 's/==.*//' requirements.txt
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        rm -f requirements.new.txt
        for package in $(cat requirements.txt)
        do
            pip freeze | grep "^${package}=" >> requirements.new.txt
        done
        diff requirements.orig.txt requirements.new.txt || :
        mv requirements.new.txt requirements.txt
        rm -f requirements.orig.txt
        deactivate
        rm -rf .venv
        cd ..
    fi
done
