FROM hashicorp/terraform:latest
RUN apk upgrade --no-cache

COPY tf-plugins /tf-plugins/

RUN apk add --no-cache aws-cli
