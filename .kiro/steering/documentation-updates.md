# Documentation Updates Rule

## Purpose
Ensure that documentation in the `docs/` folder stays synchronized with code changes and accurately reflects the current state of the system.

## Rule

WHEN making changes to the codebase, you MUST:

1. **Identify if documentation needs updating:**
   - API endpoint changes (new endpoints, modified parameters, response structures)
   - Architecture or infrastructure changes
   - New features or functionality
   - Changes to workflows or processes
   - Configuration changes
   - Authentication or authorization changes
   - Database schema or data model changes
   - Deployment procedures
   - Development setup or tooling changes

2. **Ask the user:**
   - "This change affects [area]. Would you like me to update the documentation in the `docs/` folder to reflect these changes?"
   - Wait for explicit confirmation (yes/no)

3. **If user says YES:**
   - Locate the relevant documentation file(s) in `docs/`
   - Update the documentation to accurately reflect the changes
   - Ensure examples, code snippets, and API references are current
   - Update any affected guides or tutorials
   - Maintain consistency with existing documentation style

4. **If user says NO:**
   - Proceed without updating documentation
   - Note that documentation may be out of sync

## Documentation Structure

```
docs/
├── README.md                          # Documentation index
├── design-system.md                   # UI/UX design system
├── design-system-setup.md             # Design system implementation
├── design-system-showcase-guide.md    # Design system usage guide
├── guides/                            # How-to guides
│   ├── admin/                         # Admin-specific guides
│   ├── development/                   # Development guides
│   ├── operations/                    # Operational guides
│   ├── setup/                         # Setup and installation
│   ├── EMAIL_*.md                     # Email system documentation
│   ├── PAYMENT_*.md                   # Payment system documentation
│   ├── GDPR_COMPLIANCE.md             # GDPR compliance guide
│   └── ...
├── reference/                         # Technical reference
│   ├── api-endpoints.md               # API endpoint documentation
│   ├── auth-api.md                    # Authentication API reference
│   ├── auth.md                        # Authentication system
│   ├── commands.md                    # CLI commands reference
│   ├── project-structure.md           # Project organization
│   ├── terminology.md                 # System terminology
│   └── ...
└── archived/                          # Historical documentation
```

## Common Documentation Updates

### API Changes
**When:** Adding/modifying/removing API endpoints
**Update:** `docs/reference/api-endpoints.md`, `docs/reference/auth-api.md`
**Include:** Endpoint path, method, parameters, request/response examples, error codes

### Feature Changes
**When:** Adding new features or modifying existing functionality
**Update:** Relevant guides in `docs/guides/`
**Include:** Feature description, usage instructions, examples, screenshots if applicable

### Architecture Changes
**When:** Modifying infrastructure, database schema, or system architecture
**Update:** `docs/reference/project-structure.md`, relevant technical docs
**Include:** Architecture diagrams, component descriptions, data flow

### Configuration Changes
**When:** Adding/modifying environment variables, config files, or settings
**Update:** Setup guides in `docs/guides/setup/`, `docs/guides/ENV_FILES_GUIDE.md`
**Include:** Configuration options, default values, examples

### Process Changes
**When:** Modifying deployment, development, or operational procedures
**Update:** Relevant guides in `docs/guides/operations/`, `docs/guides/development/`
**Include:** Step-by-step instructions, commands, troubleshooting tips

### Authentication/Authorization Changes
**When:** Modifying auth flows, permissions, or access control
**Update:** `docs/reference/auth.md`, `docs/reference/auth-api.md`
**Include:** Auth flows, permission matrices, role descriptions

## Examples of Changes Requiring Documentation Updates

✅ **DO ask about documentation updates for:**
- New API endpoints or modified endpoint contracts
- New features visible to users or admins
- Changes to deployment or development workflows
- Infrastructure or architecture changes
- New configuration options or environment variables
- Changes to authentication or authorization
- Database schema changes affecting API contracts
- New CLI commands or tools
- Changes to payment or email systems
- GDPR or compliance-related changes

❌ **DON'T ask for:**
- Internal code refactoring without behavior changes
- Bug fixes that restore documented behavior
- UI styling changes (unless design system changes)
- Minor code optimizations
- Test-only changes

## Documentation Quality Standards

When updating documentation:
- **Clear and concise:** Use simple language, avoid jargon
- **Complete examples:** Include working code snippets and API examples
- **Current and accurate:** Ensure all information reflects current implementation
- **Well-organized:** Follow existing structure and formatting
- **Properly linked:** Cross-reference related documentation
- **Version-aware:** Note if features are environment-specific (dev/prod)

## Verification Checklist

Before completing a task that affects documentation:
- [ ] Identified which documentation files are affected
- [ ] Asked user if documentation should be updated
- [ ] Updated all relevant documentation files
- [ ] Verified examples and code snippets are current
- [ ] Checked cross-references and links
- [ ] Maintained consistent formatting and style
- [ ] Noted any version or environment-specific information

## Red Flags

🚩 Adding new API endpoints without updating `api-endpoints.md`
🚩 Changing authentication flow without updating `auth.md`
🚩 Modifying deployment process without updating operational guides
🚩 Adding new environment variables without updating setup guides
🚩 Changing payment logic without updating payment documentation
🚩 Modifying email system without updating email guides

## Accountability

Before marking a task complete, explicitly state:
- "Code updated: [what changed]"
- "Documentation checked: [which files were reviewed]"
- "Documentation updated: [what was changed]" OR "No documentation updates needed because [reason]"

## Examples

### Example 1: New API Endpoint

**Code change:**
```python
# Added new endpoint: GET /api/boats/{boat_id}/crew-summary
```

**Documentation update:**
```markdown
<!-- docs/reference/api-endpoints.md -->

### Get Boat Crew Summary
**Endpoint:** `GET /api/boats/{boat_id}/crew-summary`
**Authentication:** Required (Team Manager or Admin)
**Description:** Returns a summary of crew members assigned to a boat

**Response:**
\`\`\`json
{
  "boat_id": "BOAT123",
  "total_crew": 9,
  "crew_by_role": {
    "Barreur": 1,
    "Rameur": 8
  }
}
\`\`\`
```

### Example 2: Configuration Change

**Code change:**
```python
# Added new environment variable: ENABLE_SLACK_NOTIFICATIONS
```

**Documentation update:**
```markdown
<!-- docs/guides/ENV_FILES_GUIDE.md -->

### ENABLE_SLACK_NOTIFICATIONS
**Type:** Boolean
**Default:** `false`
**Description:** Enable Slack notifications for payment events
**Example:** `ENABLE_SLACK_NOTIFICATIONS=true`
```

### Example 3: Feature Change

**Code change:**
```python
# Modified age category calculation to exclude coxswains
```

**Documentation update:**
```markdown
<!-- docs/reference/terminology.md -->

### Age Categories
Age categories are determined by the **oldest rower** (excluding coxswains):
- **SM (Senior Men/Mixed):** Oldest rower is under 55 years
- **VM (Veteran Men/Mixed):** Oldest rower is 55 years or older

Note: Coxswains are excluded from age category calculation.
```

## Integration with Other Rules

This rule works alongside:
- **requirements-sync.md:** Requirements document business logic, docs explain implementation
- **backend-frontend-alignment.md:** Docs should reflect both backend and frontend behavior
- **test-after-backend-changes.md:** Document testing procedures and test coverage

---

**Remember:** Documentation is code. Keep it current, accurate, and helpful.
