ARGUMENT_DATA_TYPE_UNKNOWN = 0
ARGUMENT_DATA_TYPE_BOOLEAN = 1
ARGUMENT_DATA_TYPE_INTEGER = 2
ARGUMENT_DATA_TYPE_FLOAT = 3
ARGUMENT_DATA_TYPE_COMPLEX = 4
ARGUMENT_DATA_TYPE_STRING = 5
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

UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID = (
	"newsletter[newsletter_id]",
	"newsletter[newsletter_send_id]",
	"newsletter[newsletter_user_list_id]",
)