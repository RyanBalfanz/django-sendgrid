ARGUMENT_DATA_TYPE_UNKNOWN = 0
ARGUMENT_DATA_TYPE_BOOLEAN = 1
ARGUMENT_DATA_TYPE_INTEGER = 2
ARGUMENT_DATA_TYPE_FLOAT = 3
ARGUMENT_DATA_TYPE_COMPLEX = 4
ARGUMENT_DATA_TYPE_STRING = 5
EVENT_SHORT_DESC_MAX_LENGTH = 32

EVENT_TYPES_FIELDS_MAP = {
	"UNKNOWN": None,
	"DEFERRED": ("event", "email", "response", "attempt", "category"),
	"PROCESSED": ("event", "email", "category"),
	"DROPPED": ("event", "email", "reason", "category"),
	"DELIVERED": ("event", "email", "response", "category"),
	"BOUNCE": ("event", "email", "status", "reason", "type", "category"),
	"OPEN": ("event", "email", "category"),
	"CLICK": ("event", "email", "url", "category"),
	"UNSUBSCRIBE": ("event", "email", "category"),
	"SPAMREPORT": ("event", "email", "category"),
}
