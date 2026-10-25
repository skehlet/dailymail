# README

image
![DailyMail diagram](./dailymail.png "DailyMail diagram")

## Development Setup

### Install the Project

Install `uv`, then sync the Python 3.13 environment from the lock file:

```sh
brew install uv
uv sync
```

Run commands inside that environment without activating it:

```sh
uv run python -m unittest discover -s tests -v
```

All Lambda stages and shared modules are installed from the root `src` directory. Imports such as these work across the project:

```python
from dailymail_shared.my_s3 import upload_file
from dailymail_shared.my_parameter_store import get_parameter
```

### Build the Lambda Image

Regenerate the deployment requirements after changing dependencies, then build
the shared Linux ARM64 image:

```sh
uv lock
uv export --locked --no-dev --no-emit-project --no-header --format requirements.txt --output-file requirements.txt
docker buildx build --platform linux/arm64 --provenance=false --load -t dailymail:py313-arm64 .
```

The image contains all four handlers. Lambda overrides its command per function
with one of `rss_reader.index.handler`, `scraper.index.handler`,
`summarizer.index.handler`, or `digest.index.handler`.


## Google Alert Memory

Google Alert feeds are checked against a per-topic ledger of facts already sent, so the
digest only reports genuinely new developments (new, changed, confirmed, or contradicted)
in a "What's New" section. Topics with nothing new are omitted. Ledgers are updated only
after the email is sent. If the check fails for a topic, its articles are included
unfiltered.

Ledgers are hand-editable JSON in a versioned bucket, one file per topic:

```sh
aws s3 ls s3://skehlet-dailymail-alert-ledger/alerts/
aws s3 cp s3://skehlet-dailymail-alert-ledger/alerts/gta-6-pc-release-date.json -
```

A feed's `context` in the RSS feed config is passed along as what you want to know about
the topic (e.g. "Tell me when an official PC release date is announced").
