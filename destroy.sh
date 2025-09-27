#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="cab432-core-iac"
REGION="ap-southeast-2"

aws cloudformation delete-stack \
  --region "$REGION" \
  --stack-name "$STACK_NAME"

echo "Waiting for delete to complete..."
aws cloudformation wait stack-delete-complete \
  --region "$REGION" \
  --stack-name "$STACK_NAME"
echo "Deleted."
