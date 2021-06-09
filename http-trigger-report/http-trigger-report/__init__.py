import logging
import datetime
import json
import uuid

import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

CONNECTION_STR = "Endpoint=sb://test-ucu.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lk+fUlxaTNXNmjGJ4aWQazOFCDT5yA78+6NErPz7ofI="
QUEUE_NAME = "user-reports"


def main(req: func.HttpRequest) -> func.HttpResponse:
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=CONNECTION_STR, logging_enable=True)
    url = req.params.get('url')
    status_code = req.params.get('status_code')

    if url and status_code:
        utc_timestamp = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc).isoformat()

        content = {"id": str(uuid.uuid1()),
                   "url": url,
                   "status": status_code,
                   "timestamp": utc_timestamp,
                   "is_from_user": True}

        with servicebus_client:
            sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
            with sender:
                sb_message = ServiceBusMessage(json.dumps(content))
                sender.send_messages(sb_message)

        return func.HttpResponse("Sucessfully reported about incident!")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass parameters in the query string or in the request body for sending report.",
            status_code=200
        )
