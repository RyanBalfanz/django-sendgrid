ARGUMENT_DATA_TYPE_UNKNOWN = 0
ARGUMENT_DATA_TYPE_BOOLEAN = 1
ARGUMENT_DATA_TYPE_INTEGER = 2
ARGUMENT_DATA_TYPE_FLOAT = 3
ARGUMENT_DATA_TYPE_COMPLEX = 4
ARGUMENT_DATA_TYPE_STRING = 5
EVENT_SHORT_DESC_MAX_LENGTH = 32

EVENT_FIELDS = ("event","category","email")

EVENT_MODEL_NAMES = {
	"click": "ClickEvent",
	"bounce": "BounceEvent",
	"deferred":"DeferredEvent",
	"dropped":"DroppedEvent",
	"delivered":"DeliverredEvent",
	"unknown":"Event",
	"processed":"Event",
	"open":"Event",
	"unsubscribe":"Event",
	"spamreport":"Event"
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