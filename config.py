# Configuration file for bounce-house

# Configuration variables for bounce.py
bounce_redirect_url = "http://harperrules.com/domain/?domain="
bounce_url = "http://harperrules.com/"

# Configuration for rate limiting
rate_limit = {
    "enabled": True,
    "requests": 100,
    "period": 60  # in seconds
}
