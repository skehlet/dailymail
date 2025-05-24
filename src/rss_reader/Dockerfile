FROM public.ecr.aws/lambda/python:3.12
COPY rss_reader/ ${LAMBDA_TASK_ROOT}
COPY shared/ ${LAMBDA_TASK_ROOT}/shared
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt
CMD [ "index.handler" ]
