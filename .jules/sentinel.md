## 2024-05-23 - [CORS Misconfiguration]
**Vulnerability:** The backend was configured with `allow_origins=["*"]`, allowing any domain to access the API.
**Learning:** This is a common default for development but dangerous for production as it bypasses Same-Origin Policy.
**Prevention:** Use environment variables to define allowed origins and default to a safe value (like localhost) instead of a wildcard.
