FROM public.ecr.aws/lambda/python:3.12
COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Pre-install the NLTK packages for the unstructured library:
RUN python -c "import nltk; \
    nltk.download('punkt_tab',                      download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
    nltk.download('averaged_perceptron_tagger',     download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
    nltk.download('averaged_perceptron_tagger_eng', download_dir='${LAMBDA_TASK_ROOT}/nltk_data')" \
    && rm -f ${LAMBDA_TASK_ROOT}/nltk_data/tokenizers/*.zip
ENV NLTK_DATA=nltk_data

CMD [ "index.handler" ]
