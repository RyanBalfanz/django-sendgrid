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
