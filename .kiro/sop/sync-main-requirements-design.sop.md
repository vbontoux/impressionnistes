# Sync Main Requirements and Design with Breakdowns

## Overview

This SOP ensures the main system requirements and design documents remain consistent with breakdown specifications. The main documents in `.kiro/specs/impressionnistes-registration-system/` serve as the authoritative source of truth that must reflect all changes from breakdown folders. This process maintains a coherent, up-to-date reference for stakeholders and development teams.

## Parameters

- **main_folder** (required): Path to the main requirements/design folder
  - Default: `.kiro/specs/impressionnistes-registration-system`
  - Contains: `requirements.md` and `design.md`

- **breakdown_folders** (required): List of breakdown specification folders
  - Location: All folders in `.kiro/specs/` except the main folder
  - Each contains: `requirements.md` and `design.md`

**Constraints for parameter acquisition:**
- You MUST identify all breakdown folders automatically by listing `.kiro/specs/` directory
- You MUST exclude the main folder from the breakdown list
- You MUST exclude any folders that don't contain both `requirements.md` and `design.md`
- You MUST NOT process task-related files or folders

## Steps

### 1. Identify Breakdown Folders

List all folders in `.kiro/specs/` and identify which are breakdown folders (all except the main folder).

**Constraints:**
- You MUST list the `.kiro/specs/` directory
- You MUST exclude `.kiro/specs/impressionnistes-registration-system` from processing
- You MUST verify each folder contains both `requirements.md` and `design.md`
- You MUST create a list of valid breakdown folders for processing
- You MUST log the number of breakdown folders found

### 2. Analyze Each Breakdown

For each breakdown folder, read and analyze the `requirements.md` and `design.md` files to understand what changes or additions they introduce.

**Constraints:**
- You MUST read both `requirements.md` and `design.md` from each breakdown folder
- You MUST identify the specific functional areas or features addressed by the breakdown
- You MUST note any new requirements, design patterns, or architectural decisions
- You MUST identify any modifications to existing requirements or designs
- You MUST NOT process task files or implementation details
- You SHOULD create a summary of key changes for each breakdown

### 3. Compare with Main Documents

Compare each breakdown's requirements and design against the main documents to identify gaps, inconsistencies, or missing information.

**Constraints:**
- You MUST read the current main `requirements.md` and `design.md`
- You MUST identify requirements in breakdowns that are missing from main documents
- You MUST identify design decisions in breakdowns that are missing from main documents
- You MUST identify any contradictions between breakdowns and main documents
- You MUST identify any outdated information in main documents
- You SHOULD categorize findings as: additions, modifications, or clarifications
- You SHOULD prioritize findings by impact (high, medium, low)

### 4. Determine Required Updates

Based on the comparison, determine what updates are needed to the main requirements and design documents.

**Constraints:**
- You MUST create a list of specific updates needed for `requirements.md`
- You MUST create a list of specific updates needed for `design.md`
- You MUST specify the exact location in main documents where updates should be made
- You MUST preserve the existing structure and format of main documents
- You MUST ensure updates maintain consistency with the overall system architecture
- You MUST NOT duplicate information that already exists in main documents
- You SHOULD group related updates together
- You SHOULD provide rationale for each proposed update

### 5. Update Main Requirements Document

Apply the identified updates to the main `requirements.md` file.

**Constraints:**
- You MUST maintain the existing document structure (sections, numbering, format)
- You MUST add new requirements in the appropriate sections
- You MUST update existing requirements if breakdowns provide clarifications
- You MUST preserve all existing glossary terms and add new ones if needed
- You MUST maintain consistency in requirement writing style (SHALL, MUST, WHEN/THEN)
- You MUST update appendices if breakdowns introduce new reference data
- You MUST NOT remove existing requirements without explicit justification
- You SHOULD add cross-references between related requirements
- You SHOULD update the introduction if scope has expanded

### 6. Update Main Design Document

Apply the identified updates to the main `design.md` file.

**Constraints:**
- You MUST maintain the existing document structure (sections, architecture diagrams)
- You MUST add new components, interfaces, or patterns introduced by breakdowns
- You MUST update existing design sections if breakdowns provide implementation details
- You MUST maintain consistency in terminology (especially database/API vs UI terms)
- You MUST update data models if breakdowns introduce new entities or fields
- You MUST update architecture diagrams if breakdowns introduce new components
- You MUST preserve existing design decisions unless breakdowns explicitly supersede them
- You MUST NOT remove existing design patterns without explicit justification
- You SHOULD add code examples for new patterns
- You SHOULD update the component inventory if new components are introduced

### 7. Verify Consistency

Review the updated main documents to ensure internal consistency and completeness.

**Constraints:**
- You MUST verify all cross-references between requirements and design are valid
- You MUST verify terminology is used consistently throughout both documents
- You MUST verify all requirements have corresponding design elements
- You MUST verify all design elements trace back to requirements
- You MUST verify numbering and section references are correct
- You MUST verify glossary terms are used consistently
- You SHOULD check for duplicate or redundant information
- You SHOULD verify all appendices are up to date

### 8. Generate Sync Report

Create a summary report documenting what was updated and why.

**Constraints:**
- You MUST create a report listing all changes made to main documents
- You MUST include the source breakdown folder for each change
- You MUST categorize changes as: additions, modifications, clarifications, or corrections
- You MUST provide a summary of the overall impact of the sync
- You MUST list any unresolved inconsistencies or questions
- You SHOULD include statistics (number of requirements added, sections updated, etc.)
- You SHOULD highlight any significant architectural or scope changes
- You SHOULD save the report to `.kiro/sop/sync-reports/` with timestamp

## Examples

### Example: Identifying a Missing Requirement

**Breakdown** (`.kiro/specs/ui-consistency/requirements.md`):
```
### Requirement 1: Standardized Action Button Styling
WHEN displaying action buttons in card view, THE System SHALL render them with consistent sizing:
- Minimum height: 44px (touch-friendly)
- Padding: 0.75rem 1rem
```

**Main Document Check**: Search main `requirements.md` for button styling requirements.

**Finding**: Main document has general UI requirements but lacks specific button sizing standards.

**Update**: Add new requirement or update existing UI requirement to include button sizing specifications.

### Example: Identifying a Design Addition

**Breakdown** (`.kiro/specs/admin-club-managers/design.md`):
```python
class AdminClubManagerStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        # New Lambda function for admin club manager management
        self.admin_club_manager_function = lambda_.Function(...)
```

**Main Document Check**: Search main `design.md` for admin club manager components.

**Finding**: Main design document doesn't include admin club manager Lambda function.

**Update**: Add new Lambda function to the backend functions section with appropriate documentation.

### Example: Identifying a Terminology Clarification

**Breakdown** (`.kiro/specs/boat-club-display/requirements.md`):
```
The system uses "boat" in database/API but displays "Crew" in UI when referring to team registrations.
```

**Main Document Check**: Verify terminology mapping section in main `requirements.md`.

**Finding**: Main document has terminology mapping but breakdown provides additional context.

**Update**: Enhance terminology mapping section with additional examples and clarifications from breakdown.

## Troubleshooting

### Issue: Conflicting Requirements Between Breakdowns

If two breakdowns have conflicting requirements:
- Document the conflict in the sync report
- Analyze which requirement is more recent or authoritative
- Consult with stakeholders if necessary
- Update main document with the resolved requirement
- Add a note explaining the resolution

### Issue: Breakdown Introduces Breaking Change

If a breakdown introduces a change that contradicts existing main requirements:
- Flag this as a high-priority finding
- Document the breaking change clearly
- Assess impact on existing system
- Update main document only after stakeholder approval
- Add migration notes if applicable

### Issue: Unclear Scope of Breakdown

If a breakdown's scope or relationship to main system is unclear:
- Document the ambiguity in the sync report
- Make best-effort updates based on available information
- Flag for clarification with stakeholders
- Add TODO comments in main documents if needed

### Issue: Duplicate Information Across Breakdowns

If multiple breakdowns contain similar or overlapping information:
- Consolidate the information in the main document
- Ensure the consolidated version captures all nuances
- Cross-reference the source breakdowns
- Note any variations or context-specific details

## Notes

- This SOP focuses on requirements and design documents only, not implementation tasks
- The main documents serve as the single source of truth for the overall system
- Breakdowns provide detailed specifications for specific features or areas
- Regular syncing (e.g., after completing each breakdown) keeps main documents current
- The sync process is iterative and may require multiple passes for complex changes
- Always preserve the existing structure and format of main documents
- When in doubt, favor additions over modifications to avoid losing information
- Document any assumptions or decisions made during the sync process
