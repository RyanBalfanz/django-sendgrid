ARGUMENT_DATA_TYPE_UNKNOWN = 0
ARGUMENT_DATA_TYPE_BOOLEAN = 1
ARGUMENT_DATA_TYPE_INTEGER = 2
ARGUMENT_DATA_TYPE_FLOAT = 3
ARGUMENT_DATA_TYPE_COMPLEX = 4
ARGUMENT_DATA_TYPE_STRING = 5

BATCHED_EVENT_SEPARATOR = "\r\n"

EVENT_SHORT_DESC_MAX_LENGTH = 32

EVENT_FIELDS = ("event","category","email")

EVENT_MODEL_NAMES = {
	"CLICK": "ClickEvent",
	"BOUNCE": "BounceEvent",
	"DEFERRED":"DeferredEvent",
	"DELIVERED":"DeliverredEvent",
	"DROPPED":"DroppedEvent",
	"UNKNOWN":"Event",
	"PROCESSED":"Event",
	"OPEN":"Event",
	"UNSUBSCRIBE":"Event",
	"SPAMREPORT":"Event"
}

EVENT_TYPES_EXTRA_FIELDS_MAP = {
	"UNKNOWN": (),
	"DEFERRED": ("response", "attempt"),
	"PROCESSED": (),
	"DROPPED": ("reason",),
	"DELIVERED": ("response",),
	"BOUNCE": ("status", "reason", "type"),
	"OPEN": (),
	"CLICK": ("url", ),
	"UNSUBSCRIBE": (),
	"SPAMREPORT": (),
}

NEWSLETTER_UNIQUE_IDENTIFIER = "newsletter[newsletter_id]"
UNIQUE_ARGS_STORED_FOR_NEWSLETTER_EVENTS = (
	"newsletter[newsletter_id]",
	"newsletter[newsletter_send_id]",
	"newsletter[newsletter_user_list_id]",
)

TEST_SENDER_EMAIL = "ryan@example.com"
TEST_RECIPIENTS = ["ryan@example.com", "tom@example.com","anotherguy@example.com"]

SAMPLE_NEWSLETTER_IDS = {
	"newsletter_send_id": "952852", 
	"newsletter_id": "916273", 
	"newsletter_user_list_id": "5059777"
}

SAMPLE_NEWSLETTER_IDS_2 = {
	"newsletter_send_id": "666", 
	"newsletter_id": "4324324", 
	"newsletter_user_list_id": "2344324"
}

SAMPLE_EVENT_DICT_WITHOUT_MESSAGE_ID_OR_TIMESTAMP = {
	"email": TEST_RECIPIENTS[0],
	"category":["category1"],
	"event": "OPEN"
}

