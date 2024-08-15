FROM public.ecr.aws/lambda/python:3.12
COPY . ${LAMBDA_TASK_ROOT}

# TODO: remove this once https://github.com/nltk/nltk/issues/3301 is resolved. See requirements.txt.
RUN dnf install -y git \
  	&& dnf clean all \
  	&& rm -rf /var/cache/yum

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Pre-install the NLTK packages for the unstructured library:
RUN python -c "import nltk; \
    nltk.download('punkt',                      download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
    nltk.download('averaged_perceptron_tagger', download_dir='${LAMBDA_TASK_ROOT}/nltk_data')" \
    && rm -f ${LAMBDA_TASK_ROOT}/nltk_data/tokenizers/*.zip
ENV NLTK_DATA=nltk_data

CMD [ "index.handler" ]
