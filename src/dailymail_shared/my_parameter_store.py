import boto3


def get_value_from_parameter_store(parameter):
    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=parameter, WithDecryption=True)
    return response["Parameter"]["Value"]
