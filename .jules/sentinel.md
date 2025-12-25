## 2024-05-23 - Overly Permissive CORS Configuration
**Vulnerability:** The backend was configured with `allow_origins=["*"]` and `allow_credentials=True`. This configuration is insecure as it allows any website to make authenticated requests to the backend, potentially leading to data theft or unauthorized actions if the user is authenticated (e.g., via cookies).
**Learning:** Hardcoding `allow_origins=["*"]` is a common mistake in development that often makes it to production. It defeats the purpose of Same-Origin Policy.
**Prevention:** Always use an environment variable (e.g., `CORS_ORIGINS`) to define allowed origins. Default to a safe local development URL (e.g., `http://localhost:3000`) if the variable is not set, but never default to `*`.
