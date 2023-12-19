FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY check_vitals.py ${LAMBDA_TASK_ROOT}


CMD [ "check_vitals.handler" ]