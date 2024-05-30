FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

RUN apt-get update && apt-get -y upgrade && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ \
    "python", \
    "main.py", \
]






FROM public.ecr.aws/lambda/python:3.12

COPY src/rss_reader ${LAMBDA_TASK_ROOT}

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# # TODO: remove this once langchain is updated for Bedrock+Mistral
# COPY src/misc/patched-bedrock.py ${LAMBDA_TASK_ROOT}
# RUN mv ${LAMBDA_TASK_ROOT}/patched-bedrock.py /var/lang/lib/python3.12/site-packages/langchain_aws/chat_models/bedrock.py

# # Pre-install the NLTK packages for the unstructured library:
# RUN python -c "import nltk; \
#     nltk.download('punkt',                      download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
#     nltk.download('averaged_perceptron_tagger', download_dir='${LAMBDA_TASK_ROOT}/nltk_data')" \
#     && rm -f ${LAMBDA_TASK_ROOT}/nltk_data/tokenizers/*.zip
# ENV NLTK_DATA=nltk_data

# # Pre-install the `gpt2` tokenizer for the LangChain map-reduce summarizer:
# # TODO: still needed since I removed map/reduce?
# ENV HF_HOME=/var/huggingface
# RUN python -c "from transformers import AutoTokenizer; \
#     tokenizer = AutoTokenizer.from_pretrained('gpt2')"

CMD [ "index.handler" ]
