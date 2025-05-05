FROM public.ecr.aws/lambda/python:3.12
RUN pip install poetry
WORKDIR ${LAMBDA_TASK_ROOT}
COPY ./digest/ ./digest/
COPY ./shared/ ./shared/
WORKDIR ${LAMBDA_TASK_ROOT}/digest
RUN poetry install --no-interaction --no-ansi
CMD [ "index.handler" ]
