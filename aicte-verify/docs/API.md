# AICTE-Verify API Documentation

## Base URL
- Development: `http://localhost:8000`
- API docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All endpoints (except `/auth/login` and `/health`) require a JWT Bearer token.

### Login
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```
Authorization: Bearer eyJ...
```

## Endpoints Summary

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | None | Login, returns JWT |
| POST | `/auth/register` | Admin | Register new user |
| GET | `/auth/me` | Any | Current user info |

### Applications
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/applications/` | Any | List applications (filtered by role) |
| POST | `/applications/` | College | Create application |
| GET | `/applications/{id}` | Any | Application detail |
| PUT | `/applications/{id}/status` | Officer/Admin | Update status |
| GET | `/applications/{id}/validation-report` | Any | Validation report |
| GET | `/applications/{id}/risk-breakdown` | Any | Risk score breakdown |
| POST | `/applications/{id}/resubmit` | College | Resubmit with changes |

### Documents
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/documents/upload` | Any | Upload document |
| GET | `/documents/{id}` | Any | Document metadata |
| GET | `/documents/{id}/content` | Any | Serve file |
| GET | `/documents/{id}/evidence` | Any | Evidence view data |
| POST | `/documents/{id}/reupload` | College | Replace document |
| POST | `/documents/{id}/process` | Any | Trigger processing |
| GET | `/documents/{id}/forensics` | Any | Forensics results |

### Verification (SIMULATED)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/verify/{document_id}` | Officer/Admin | Trigger verification |
| GET | `/verify/results/{document_id}` | Any | Verification results |
| GET | `/verify/queue` | Officer/Admin | Manual review queue |

### Compliance
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/compliance/check/{application_id}` | Officer/Admin | Run compliance check |
| GET | `/compliance/results/{application_id}` | Any | Compliance results |
| GET | `/compliance/capacity/{application_id}` | Any | Intake capacity calculator |

### Flags
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/flags/` | Any | All flags |
| GET | `/flags/{application_id}` | Any | Flags for application |
| PUT | `/flags/{id}/resolve` | Officer/Admin | Resolve flag (confirmation required) |
| GET | `/alerts/` | Any | Active alerts |

### Audit
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/audit/` | Admin | Paginated audit log |
| GET | `/audit/verify-chain` | Admin | Verify chain integrity |
| POST | `/audit/simulate-tamper` | Admin (dev) | Simulate tampering |

### Analytics
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/analytics/summary` | Any | Dashboard summary |
| GET | `/analytics/flags-by-type` | Any | Flag distribution |
| GET | `/analytics/verification-outcomes` | Any | Verification stats |
| GET | `/analytics/processing-times` | Any | Processing time stats |

### Knowledge Graph
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/graph/entities` | Any | All graph entities |
| GET | `/graph/relations` | Any | All relations |
| GET | `/graph/institution/{id}` | Any | Subgraph for institution |
| GET | `/graph/flagged` | Any | Flagged relationships only |

### Letters
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/letters/generate/{application_id}` | Officer/Admin | Generate deficiency letter |
| POST | `/letters/improve` | Officer/Admin | Improve wording (requires Gemini API key) |
| PUT | `/letters/{id}/approve` | Officer/Admin | Approve letter |

### Mock Issuer (SIMULATED)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/mock-issuer/verify/{doc_type}/{ref_number}` | Any | Verify certificate |
| GET | `/mock-issuer/registry` | Admin | List registry |
| POST | `/mock-issuer/register` | Admin | Add to registry |

### Users (Admin)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/` | Admin | List users |
| PUT | `/users/{id}/role` | Admin | Change role |
| DELETE | `/users/{id}` | Admin | Deactivate user |

### Evaluation
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/evaluation/results` | Any | Evaluation metrics |
| POST | `/evaluation/run` | Admin | Trigger evaluation |

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient role)
- `404` - Not found
- `422` - Validation error
- `500` - Internal server error
