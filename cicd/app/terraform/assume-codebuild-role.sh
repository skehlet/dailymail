# Assume the CodeBuild role
# Source this script

MY_AWS_ACCOUNT_ID=519765885403

if read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN \
    < <(aws sts assume-role \
        --role-arn arn:aws:iam::${MY_AWS_ACCOUNT_ID}:role/DailyMailPipeline-CodeBuildRole \
        --role-session-name assume-$(date +%s) \
        --output text \
        --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]')
then
    export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    export AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
    unset AWS_PROFILE
    aws sts get-caller-identity
else
    unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
fi

unset MY_AWS_ACCOUNT_ID
