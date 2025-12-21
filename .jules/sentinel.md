## 2024-05-23 - Overly Permissive CORS Configuration
**Vulnerability:** The backend was configured with `allow_origins=["*"]` and `allow_credentials=True` in `backend/main.py`. This is a High Severity vulnerability that allows any malicious website to make authenticated requests to the API on behalf of a user.
**Learning:** Development configurations often leak into production codebases. "Configure for production" comments are insufficient; secure defaults must be enforced in code.
**Prevention:** Always use environment variables for CORS configuration and default to a restrictive list (e.g., localhost). Never commit `allow_origins=["*"]` when `allow_credentials=True`.
