#!/bin/sh
set -e

echo "Creating SQS queues..."
awslocal sqs create-queue --queue-name order-events >/dev/null
awslocal sqs create-queue --queue-name inventory-events >/dev/null

echo "SQS queues ready."
