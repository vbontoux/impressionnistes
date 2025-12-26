# Project Structure

## Overview

Simplified project structure for the Course des Impressionnistes Registration System.

## Terminology Note

> **Important:** In the codebase (API, database, backend), "boat" refers to a crew registration (the team of rowers). In the user interface, this is displayed as "Crew" (English) or "Équipage" (French). The term "boat" is only used in the UI when referring to physical equipment (boat types, boat rentals).
>
> **Examples:**
> - `boat_registration` (database) → "Crew" (UI)
> - `boat_id` (API) → Internal identifier, not shown in UI
> - `boat_type` (database/UI) → "Boat Type" (refers to physical boat: skiff, four, eight)
>
> See the [Requirements Document](../../.kiro/specs/impressionnistes-registration-system/requirements.md#terminology-mapping-databaseapi-vs-ui) for complete details.

## Directory Structure

```
impressionnistes/
├── functions/                 # Lambda functions and shared utilities
│   ├── shared/               # Shared Python modules (Lambda Layer)
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication utilities
│   │   ├── database.py      # DynamoDB utilities
│   │   ├── responses.py     # Standardized API responses
│   │   ├── validation.py    # Input validation with Cerberus
│   │   └── configuration.py # Configuration management
│   │
│   ├── auth/                # Authentication functions
│   │   ├── register.py
│   │   ├── get_profile.py
│   │   ├── update_profile.py
│   │   ├── forgot_password.py
│   │   └── confirm_password_reset.py
│   │
│   ├── crew/                # Crew member management
│   ├── boat/                # Boat registration (crew registration in UI)
│   ├── payment/             # Payment processing
│   ├── admin/               # Admin operations (future)
│   ├── health/              # Health check endpoint
│   │   └── health_check.py
│   ├── init/                # Initialization functions
│   │   └── init_config.py
│   │
│   └── test_live_db.py      # Live database test script
│
├── infrastructure/           # AWS CDK infrastructure code
│   ├── stacks/              # CDK stack definitions
│   │   ├── database_stack.py
│   │   ├── auth_stack.py
│   │   ├── api_stack.py
│   │   ├── monitoring_stack.py
│   │   └── frontend_stack.py
│   ├── app.py               # CDK app entry point
│   ├── Makefile             # Deployment commands
│   └── requirements.txt     # CDK dependencies
│
├── frontend/                 # Vue.js 3 frontend (future)
│   └── src/
│
└── .kiro/                   # Kiro spec files
    └── specs/
        └── impressionnistes-registration-system/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## Key Concepts

### Simplified Structure

Everything Lambda-related is in `functions/`:
- **`functions/shared/`** - Shared utilities deployed as a Lambda Layer
- **`functions/<category>/`** - Lambda function handlers

### Why This Structure?

1. **Simplicity**: All Lambda code in one place
2. **Lambda Best Practice**: Shared code as a layer, functions import from it
3. **Clear Organization**: Easy to find both shared code and functions
4. **No Confusion**: No separate `backend/` directory

## Import Pattern

Lambda functions import shared utilities like this:

```python
# In functions/auth/register.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.responses import success_response, validation_error
from shared.validation import validate_team_manager
from shared.database import get_db_client
```

The CDK infrastructure creates a Lambda layer from `functions/shared/`:

```python
# In infrastructure/stacks/api_stack.py
self.shared_layer = lambda_.LayerVersion(
    self,
    "SharedLayer",
    code=lambda_.Code.from_asset("functions/shared"),
    compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
    description="Shared utilities for Lambda functions"
)
```

## Deployment

### Lambda Layer + Functions
Deployed together when deploying the API stack:
```bash
cd infrastructure
make deploy-api ENV=dev
```

### All Infrastructure
```bash
cd infrastructure
make deploy ENV=dev  # Deploy all stacks
```

## Development Workflow

1. **Add shared utility**: Edit files in `functions/shared/`
2. **Add Lambda function**: Create new file in `functions/<category>/`
3. **Update infrastructure**: Add function to `api_stack.py`
4. **Deploy**: Run `make deploy-api`

## Testing

### Live Database Test
```bash
cd functions
python3 test_live_db.py
```

### Lambda Functions
Lambda functions are tested via integration tests after deployment.

## Notes

- **Single Location**: All Lambda code (shared + functions) in `functions/`
- **Lambda Layer**: `functions/shared/` becomes a Lambda layer
- **Function Code**: Function handlers in `functions/<category>/`
- **Clean Structure**: No redundant `backend/` directory
