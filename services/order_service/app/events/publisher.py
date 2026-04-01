import json
import logging
import uuid
from datetime import UTC, datetime

import aioboto3

from app.models.order import Order

logger = logging.getLogger(__name__)


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

    async def publish_order_created(self, order: Order) -> None:
        payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": "ORDER_CREATED",
            "occurred_at": datetime.now(UTC).isoformat(),
            "data": {
                "order_id": str(order.id),
                "product_id": order.product_id,
                "quantity": order.quantity,
                "user_id": order.user_id,
                "status": order.status,
            },
        }

        logger.info(
            "Publishing ORDER_CREATED event",
            extra={"order_id": str(order.id), "queue_url": self.queue_url},
        )

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
                        "StringValue": "ORDER_CREATED",
                    }
                },
            )
