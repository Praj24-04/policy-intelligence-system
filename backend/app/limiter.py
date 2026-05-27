from slowapi import Limiter
from slowapi.util import get_remote_address

# Centralized Limiter instance using client remote IP address as the unique rate-limiting key
limiter = Limiter(key_func=get_remote_address)
