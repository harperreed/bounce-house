import os


class Config:
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    STAT_NAME = "domain_counter"
    STAT_DESC = "visits to domain"
    BOUNCE_REDIRECT_URL = os.environ.get(
        "BOUNCE_REDIRECT_URL", "http://harperrules.com/domain/?domain="
    )
    BOUNCE_URL = os.environ.get("BOUNCE_URL", "http://harperrules.com/")
