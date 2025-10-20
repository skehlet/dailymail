#!/bin/bash
set -e

# brew install python gnu-sed
# Be sure to close and reopen your terminal to pick up the tools in /opt/homebrew/bin

MY_DIR=$(dirname $0)
cd "$MY_DIR"

for dir in \
    digest \
    rss_reader \
    scraper \
    summarizer
do
    if [[ -f $dir/requirements.txt ]]; then
        echo $dir
        cd $dir
        cp -p requirements.txt requirements.orig.txt
        gsed -i -e 's/==.*//' requirements.txt
        rm -rf .venv
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        rm -f requirements.new.txt
        for package in $(cat requirements.txt)
        do
            pip freeze | grep "^${package}=" >> requirements.new.txt || { echo "Warning: package $package not found in pip freeze"; exit 1; }
        done
        diff requirements.orig.txt requirements.new.txt || :
        mv requirements.new.txt requirements.txt
        rm -f requirements.orig.txt
        deactivate
        rm -rf .venv
        cd ..
        echo -n "Pressed Enter to continue..."
        read junk
    fi
done
