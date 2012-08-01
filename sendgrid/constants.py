EVENT_SHORT_DESC_MAX_LENGTH = 32

EMAIL_EVENT_UNKNOWN = 0
EMAIL_EVENT_DEFERRED = 100
# Process Stage
EMAIL_EVENT_PROCESSED = 1000
EMAIL_EVENT_DROPPED = 1100
# Deliver Stage
EMAIL_EVENT_DELIVERED = 2000
EMAIL_EVENT_BOUNCED = 2100
# Read Stage
EMAIL_EVENT_OPENED = 3000
EMAIL_EVENT_CLICKED = 3100
EMAIL_EVENT_UNSUBSCRIBED = 3200
EMAIL_EVENT_SPAM = 3400

EVENT_TYPES_MAP = {
	"UNKNOWN": EMAIL_EVENT_UNKNOWN,
	"DEFERRED": EMAIL_EVENT_DEFERRED,
	"PROCESSED": EMAIL_EVENT_PROCESSED,
	"DROPPED": EMAIL_EVENT_DROPPED,
	"DELIVERED": EMAIL_EVENT_DELIVERED,
	"BOUNCE": EMAIL_EVENT_BOUNCED,
	"OPEN": EMAIL_EVENT_OPENED,
	"CLICK": EMAIL_EVENT_CLICKED,
	"UNSUBSCRIBE": EMAIL_EVENT_UNSUBSCRIBED,
	"SPAMREPORT": EMAIL_EVENT_SPAM,
}

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
