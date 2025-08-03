FROM public.ecr.aws/lambda/python:3.12

COPY dailymail_shared_package /tmp/dailymail_shared_package
RUN pip install /tmp/dailymail_shared_package

COPY src/rss_reader/ ${LAMBDA_TASK_ROOT}
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

CMD [ "index.handler" ]
