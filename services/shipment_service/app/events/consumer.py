import asyncio
import json
import logging

import aioboto3

from app.core.config import Settings
from app.db.session import AsyncSessionLocal
from app.services.shipment_service import ShipmentService

logger = logging.getLogger(__name__)


class ShipmentEventConsumer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = aioboto3.Session()

    async def run(self, stop_event: asyncio.Event) -> None:
        logger.info("Shipment consumer started")

        async with self.session.client(
            "sqs",
            region_name=self.settings.aws_region,
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            endpoint_url=self.settings.aws_endpoint_url,
        ) as sqs:
            while not stop_event.is_set():
                try:
                    response = await sqs.receive_message(
                        QueueUrl=self.settings.shipment_sqs_queue_url,
                        MaxNumberOfMessages=10,
                        WaitTimeSeconds=10,
                        MessageAttributeNames=["All"],
                    )
                except Exception:
                    logger.exception("Failed to receive messages from SQS")
                    await asyncio.sleep(2)
                    continue

                messages = response.get("Messages", [])
                for message in messages:
                    should_delete = await self._process_message(message)
                    if should_delete:
                        await sqs.delete_message(
                            QueueUrl=self.settings.shipment_sqs_queue_url,
                            ReceiptHandle=message["ReceiptHandle"],
                        )

    async def _process_message(self, message: dict) -> bool:
        try:
            body = json.loads(message["Body"])
        except (KeyError, json.JSONDecodeError):
            logger.warning("Dropping malformed message")
            return True

        event_type = body.get("event_type")
        if event_type != "INVENTORY_RESERVED":
            return True

        data = body.get("data") or {}
        order_id = str(data.get("order_id", ""))
        product_id = str(data.get("product_id", ""))

        try:
            quantity = int(data.get("quantity", 0))
        except (TypeError, ValueError):
            quantity = 0

        if not order_id or not product_id or quantity <= 0:
            logger.warning("Dropping invalid INVENTORY_RESERVED payload", extra={"body": body})
            return True

        try:
            async with AsyncSessionLocal() as db_session:
                service = ShipmentService(db_session)
                shipment = await service.create_from_inventory_reserved(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                )
        except Exception:
            logger.exception(
                "Failed to process INVENTORY_RESERVED message",
                extra={"order_id": order_id, "product_id": product_id},
            )
            return False

        logger.info(
            "Shipment created from inventory reservation",
            extra={"order_id": shipment.order_id, "shipment_id": str(shipment.id)},
        )
        return True
