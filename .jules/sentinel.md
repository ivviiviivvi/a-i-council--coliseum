## 2024-05-23 - Content-Security-Policy breaks FastAPI Docs
**Vulnerability:** Missing Content-Security-Policy (CSP) header is a security gap (High/Medium), but implementing a strict default (`default-src 'self'`) breaks FastAPI's Swagger UI (`/docs`) which relies on CDNs for JS/CSS.
**Learning:** Security controls often conflict with developer experience (DX) tools. FastAPI's auto-generated docs are a key part of the dev workflow.
**Prevention:** When implementing CSP in FastAPI projects, explicitly allow CDNs used by Swagger UI (`cdn.jsdelivr.net`, `fastapicdn.com`) or disable CSP on the `/docs` endpoint. For now, CSP is omitted to prioritize functional docs while keeping other headers.
