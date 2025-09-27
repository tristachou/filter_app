#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="cab432-core-iac"
REGION="ap-southeast-2"

# <<< replace with your QUT emails >>>
QUT_USERNAME="n11789701@qut.edu.au"
QUT_USERNAME2="n11696630@qut.edu.au"

aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --template-file infra_core.yaml \
  --parameter-overrides \
    QutUsername="$QUT_USERNAME" \
    QutUsername2="$QUT_USERNAME2" \
    EnvName="dev"

echo "Outputs:"
aws cloudformation describe-stacks \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs"
