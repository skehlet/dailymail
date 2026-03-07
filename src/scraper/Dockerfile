FROM public.ecr.aws/lambda/python:3.12

COPY dailymail_shared_package /tmp/dailymail_shared_package
RUN pip install /tmp/dailymail_shared_package

COPY src/scraper/ ${LAMBDA_TASK_ROOT}

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Pre-install the NLTK packages for the unstructured library:
RUN python -c "import nltk; \
    nltk.download('punkt_tab',                      download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
    nltk.download('averaged_perceptron_tagger',     download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
    nltk.download('averaged_perceptron_tagger_eng', download_dir='${LAMBDA_TASK_ROOT}/nltk_data')" \
    && rm -f ${LAMBDA_TASK_ROOT}/nltk_data/tokenizers/*.zip
ENV NLTK_DATA=nltk_data

# Pre-install the spaCy model for the unstructured library.
RUN python -m spacy download en_core_web_sm

CMD [ "index.handler" ]
