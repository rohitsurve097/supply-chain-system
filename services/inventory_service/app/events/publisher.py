import json
import uuid
from datetime import UTC, datetime

import aioboto3


class SqsEventPublisher:
    def __init__(
        self,
        queue_url: str,
        region_name: str,
        access_key_id: str,
        secret_access_key: str,
        endpoint_url: str,
    ) -> None:
        self.queue_url = queue_url
        self.region_name = region_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.endpoint_url = endpoint_url
        self.session = aioboto3.Session()

    async def publish_inventory_reserved(
        self,
        order_id: str,
        product_id: str,
        quantity: int,
        remaining_stock: int,
    ) -> None:
        payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": "INVENTORY_RESERVED",
            "occurred_at": datetime.now(UTC).isoformat(),
            "data": {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "remaining_stock": remaining_stock,
            },
        }

        async with self.session.client(
            "sqs",
            region_name=self.region_name,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url,
        ) as sqs:
            await sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(payload),
                MessageAttributes={
                    "event_type": {
                        "DataType": "String",
                        "StringValue": "INVENTORY_RESERVED",
                    }
                },
            )
