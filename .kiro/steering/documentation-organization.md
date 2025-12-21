---
inclusion: always
---

# Documentation Organization Rule

## Purpose
Maintain a clean, organized, and discoverable documentation structure that follows industry best practices.

## Documentation Structure

All project documentation MUST follow this structure:

```
docs/
├── guides/
│   ├── setup/              # Setup and deployment guides
│   ├── development/        # Development workflow guides
│   └── operations/         # Operations and maintenance guides
├── reference/              # Technical reference documentation
└── archived/               # Historical/deprecated documentation

Component-specific docs (stay local):
├── frontend/               # Frontend-specific implementation docs
├── infrastructure/         # Infrastructure-specific implementation docs
├── functions/              # Lambda function-specific docs
└── tests/                  # Test-specific documentation
```

## Rule: When to Move Documentation to `docs/`

### ✅ MUST Move to `docs/` When:

1. **Cross-cutting concerns** - Documentation that affects multiple parts of the system
   - Examples: Architecture decisions, deployment guides, testing strategy
   - Location: `docs/guides/` or `docs/reference/`

2. **Onboarding/setup guides** - New developers need to find these easily
   - Examples: Quick start, setup instructions, deployment procedures
   - Location: `docs/guides/setup/`

3. **System-wide operations** - Used by different roles (DevOps, admins, developers)
   - Examples: Database operations, monitoring, infrastructure management
   - Location: `docs/guides/operations/`

4. **Development workflows** - General development practices
   - Examples: Development workflow, testing guides, contribution guidelines
   - Location: `docs/guides/development/`

5. **Technical reference** - System-wide technical documentation
   - Examples: API endpoints, command reference, project structure
   - Location: `docs/reference/`

6. **Historical documentation** - No longer actively used but kept for reference
   - Examples: Old implementation notes, deprecated features, bug logs
   - Location: `docs/archived/`

### ✅ MUST Keep Local When:

1. **Component-specific implementation details** - Only relevant when working in that directory
   - Examples: Component API docs, module-specific patterns
   - Location: Same directory as the code (e.g., `frontend/src/components/README.md`)

2. **Developer workflow files** - Used during active development in that folder
   - Examples: Test event payloads, migration templates, build scripts
   - Location: Same directory as the code (e.g., `functions/auth/TEST_EVENTS.md`)

3. **Quick reference for that module** - Consulted while coding in that area
   - Examples: Environment file guide, payment testing guide
   - Location: Same directory as related files (e.g., `frontend/ENV_FILES_GUIDE.md`)

4. **Examples/test data** - Specific to that component's testing
   - Examples: Sample payloads, test fixtures, mock data
   - Location: Same directory as tests (e.g., `functions/auth/TEST_EVENTS.md`)

5. **Module README** - Overview of that specific module
   - Examples: `infrastructure/README.md`, `tests/README.md`
   - Location: Root of that module directory

## Documentation Naming Conventions

### Files in `docs/`
- Use **lowercase with hyphens**: `quick-start.md`, `dev-workflow.md`
- Be descriptive: `database-export.md` not `db.md`
- Group by purpose: `setup/`, `development/`, `operations/`

### Files in Component Directories
- Use **UPPERCASE for guides**: `ENV_FILES_GUIDE.md`, `PAYMENT_TESTING.md`
- Use **lowercase for module docs**: `README.md`, `api.md`
- Keep names short and clear

## Process for Adding New Documentation

### Step 1: Determine Documentation Type

Ask these questions:
1. **Who needs this?** (One team/role or multiple?)
2. **When is it used?** (During development in one area or across the project?)
3. **What does it document?** (Implementation detail or system-wide concept?)

### Step 2: Choose Location

**If answers indicate cross-cutting or onboarding:**
→ Move to `docs/guides/` or `docs/reference/`

**If answers indicate component-specific:**
→ Keep in component directory

### Step 3: Update README.md

**Always** add a link to new documentation in the main `README.md` under the appropriate section.

## Examples

### ✅ Correct Placement

**Cross-cutting guide → `docs/`:**
```
docs/guides/setup/deployment.md
- Used by: DevOps, developers
- Scope: Entire system deployment
- Reason: Multiple teams need this for different environments
```

**Component-specific → Local:**
```
frontend/ENV_FILES_GUIDE.md
- Used by: Frontend developers
- Scope: Frontend environment configuration only
- Reason: Only relevant when working in frontend/
```

**Implementation pattern → Local:**
```
frontend/src/utils/RESPONSIVE_TABLE_PATTERNS.md
- Used by: Frontend developers working on tables
- Scope: Specific implementation patterns for responsive tables
- Reason: Technical reference for implementing table components
```

**System reference → `docs/`:**
```
docs/reference/api-endpoints.md
- Used by: Frontend developers, backend developers, testers
- Scope: Complete API reference
- Reason: Multiple teams need to understand the API
```

### ❌ Incorrect Placement

**Don't put component-specific docs in `docs/`:**
```
❌ docs/guides/frontend-env-files.md
✅ frontend/ENV_FILES_GUIDE.md
```

**Don't put cross-cutting guides in component directories:**
```
❌ infrastructure/DEPLOYMENT_GUIDE.md
✅ docs/guides/setup/deployment.md
```

**Don't scatter related guides:**
```
❌ SETUP.md, QUICK-START.md, DEPLOYMENT.md (all at root)
✅ docs/guides/setup/setup.md
✅ docs/guides/setup/quick-start.md
✅ docs/guides/setup/deployment.md
```

## Enforcement

### When Creating New Documentation

1. **Before creating a new `.md` file**, determine its location using the rules above
2. **Create the file in the correct location** from the start
3. **Add a link** to the main `README.md` if it's in `docs/`
4. **Update related documentation** to reference the new file

### When Reviewing Pull Requests

Check that:
- [ ] New documentation is in the correct location
- [ ] File naming follows conventions
- [ ] README.md is updated if documentation is in `docs/`
- [ ] No duplicate documentation exists
- [ ] Links between documents are correct

### Periodic Cleanup

Every quarter, review:
- [ ] Are there new files at the root that should be in `docs/`?
- [ ] Are there outdated guides that should move to `docs/archived/`?
- [ ] Are all links in README.md still valid?
- [ ] Is the documentation structure still serving its purpose?

## Quick Decision Tree

```
New documentation needed
    │
    ├─ Is it specific to one component/module?
    │   └─ YES → Keep in component directory
    │
    ├─ Is it used only when working in that directory?
    │   └─ YES → Keep in component directory
    │
    ├─ Is it a setup/deployment/operations guide?
    │   └─ YES → Move to docs/guides/
    │
    ├─ Is it technical reference (API, commands, structure)?
    │   └─ YES → Move to docs/reference/
    │
    ├─ Is it outdated but worth keeping?
    │   └─ YES → Move to docs/archived/
    │
    └─ Still unsure?
        └─ Ask: "Would a new developer need this to understand the system?"
            ├─ YES → docs/guides/
            └─ NO → Keep local
```

## Benefits of This Structure

1. **Discoverability**: New developers know where to find documentation
2. **Maintainability**: Clear ownership and organization
3. **Scalability**: Structure supports growth without becoming messy
4. **Consistency**: Everyone follows the same patterns
5. **Efficiency**: Developers spend less time searching for docs

## Migration Checklist

When moving existing documentation:
- [ ] Move file to correct location in `docs/`
- [ ] Update all internal links in the moved file
- [ ] Update all references to this file in other documents
- [ ] Update README.md to point to new location
- [ ] Delete old file
- [ ] Commit with clear message: "docs: move X to docs/guides/Y"

## Examples from This Project

### Correctly Organized

✅ **`docs/guides/setup/quick-start.md`**
- Cross-cutting: Used by all new developers
- Onboarding: First thing people need

✅ **`frontend/ENV_FILES_GUIDE.md`**
- Component-specific: Only for frontend configuration
- Local reference: Used when setting up frontend

✅ **`docs/reference/commands.md`**
- Technical reference: Complete command documentation
- Cross-cutting: Used by all developers and DevOps

✅ **`functions/migrations/README.md`**
- Module-specific: Only for database migrations
- Implementation guide: Used when writing migrations

### Previously Incorrect (Now Fixed)

❌ **Was: `QUICK-START.md` (at root)**
✅ **Now: `docs/guides/setup/quick-start.md`**

❌ **Was: `infrastructure/DEPLOYMENT_GUIDE.md`**
✅ **Now: `docs/guides/setup/deployment.md`**

❌ **Was: `BUGS.md` (at root)**
✅ **Now: `docs/archived/bugs.md`**

## Summary

**The Golden Rule:**
> If it's used by multiple teams or for onboarding → `docs/`
> If it's specific to one component and used while coding there → Keep local

When in doubt, ask: "Would someone working in a different part of the codebase need this?" If yes, it belongs in `docs/`.
