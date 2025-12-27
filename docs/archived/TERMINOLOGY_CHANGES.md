# UI Terminology Changes: "Boat" → "Crew/Équipage" (SIMPLIFIED)

## Summary
Updated UI terminology to:
1. Correctly distinguish between **Crew/Équipage** (team of rowers) and **Boat** (physical equipment)
2. **Simplify expressions** by removing verbose "registration/inscription" words where context is clear

## Simplification Philosophy
- **Before:** "Create Crew Registration" / "Créer une inscription d'équipage"
- **After:** "Create Crew" / "Créer un équipage"
- **Rationale:** Context makes it clear we're creating a crew entry, no need for "registration/inscription"

## Changes Made

### English Translations (en.json)
Updated ~60 translation keys with simplified, shorter expressions:

#### Navigation & Menus
- `nav.boats`: "Boats" → "Crews"
- `nav.boatRegistrations`: "Boat Registrations" → "Crews"

#### Page Titles & Headers (Simplified)
- `boat.addNew`: "Add Boat" → "Add Crew"
- `boat.createFirst`: "Create your first boat registration" → "Create your first crew"
- `boat.noBoats`: "No boat registrations yet" → "No crews yet"
- `boat.createRegistration`: "Create Boat Registration" → "Create Crew"
- `boat.boatInformation`: "Boat Information" → "Crew Information"

#### Admin Section (Simplified)
- `admin.dashboard.totalBoatRegistrations`: "Registered Boats" → "Registered Crews"
- `admin.boats.title`: "All Boat Registrations" → "All Crews"
- `admin.boats.subtitle`: "View and manage boat registrations..." → "View and manage crews..."
- `admin.boats.addBoat`: "Add Boat" → "Add Crew"
- `admin.boats.totalCount`: "{count} boat registrations" → "{count} crews"
- `admin.boats.editBoat`: "Edit Boat" → "Edit Crew"
- `admin.boatRegistrations`: "Manage Crew Registrations" → "Manage Crews"
- `admin.boatRegistrationsDesc`: "View and manage all crew registrations" → "View and manage all crews"

#### Dashboard & Stats (Simplified)
- `dashboard.subtitle`: "Manage your crew registrations..." → "Manage your crews..."
- `dashboard.stats.boats`: "Total Boats" → "Total Crews"
- `dashboard.stats.paidBoats`: "Paid Boats" → "Paid Crews"
- `dashboard.emptyState.description`: "...then create crew registrations" → "...then create your crews"
- `dashboard.actions.manageBoats.title`: "Manage Boats" → "Manage Crews"
- `dashboard.actions.manageBoats.description`: "Register and configure your crew entries" → "Register and configure your crews"

#### Payment Section (Simplified)
- `payment.boatRegistrations`: "Boat Registrations" → "Crews"
- `payment.boatsAvailable`: "{count} boat(s) available" → "{count} crew(s) available"
- `payment.boatsSelected`: "{count} boat(s) selected" → "{count} crew(s) selected"
- `payment.checkout.noSelection`: "No boats selected" → "No crews selected"
- `payment.success.message`: "Your boats are now registered..." → "Your crews are now registered..."

#### Search & Filters (Simplified)
- `boat.filter.search`: "Search by stroke rower, boat type..." → "Search by stroke rower, crew type..."
- `boat.searchPlaceholder`: "Search by stroke rower, boat type..." → "Search by stroke rower, crew type..."

#### Messages & Confirmations (Simplified)
- `boat.confirmDelete`: "Are you sure you want to delete {name}?" → "Are you sure you want to delete crew {name}?"
- `boat.cannotDeletePaid`: "Cannot delete a paid boat..." → "Cannot delete a paid crew..."
- `boat.loadError`: "Failed to load boat registration" → "Failed to load crew"
- `boat.saveError`: "Failed to save boat registration" → "Failed to save crew"
- `boat.createError`: "Failed to create boat registration" → "Failed to create crew"

#### Data Export (Simplified)
- `admin.dataExport.totalBoats`: "Total Boats" → "Total Crews"
- `admin.dataExport.crewTimerDescription`: "Export races and boats..." → "Export races and crews..."
- `admin.dataExport.exportBoatRegistrations`: "Export Boat Registrations" → "Export Crews"
- `admin.dataExport.standardDescription`: "Export crew members and crew registrations..." → "Export crew members and crews..."
- `admin.dataExportsDesc`: "Export crew members and crew registrations" → "Export crew members and crews"

#### Timeline & Rules (Simplified)
- `home.timeline.phase1.rule2`: "Create and delete boat registrations" → "Create and delete crews"
- `home.timeline.phase2.rule1`: "Cannot delete boats anymore" → "Cannot delete crews anymore"
- `home.timeline.phase2.rule2`: "Can still pay for registered boats" → "Can still pay for registered crews"
- `home.timeline.phase2.rule3`: "Can modify existing boat details" → "Can modify existing crew details"
- `home.timeline.phase3.rule3`: "Only paid boats will be able to race" → "Only paid crews will be able to race"
- `home.timeline.notice.message`: "Only boats with confirmed payment..." → "Only crews with confirmed payment..."

#### Process Steps (Simplified)
- `home.process.step3.title`: "Create Boat Entries" → "Create Your Crews"
- `home.process.step3.description`: "...configure each boat entry..." → "...configure each crew..."

### French Translations (fr.json)
Updated ~60 translation keys with equivalent simplified French:

#### Navigation & Menus
- `nav.boats`: "Bateaux" → "Équipages"
- `nav.boatRegistrations`: "Inscriptions d'équipages" → "Équipages"

#### Page Titles & Headers (Simplified)
- `boat.addNew`: "Ajouter un bateau" → "Ajouter un équipage"
- `boat.createFirst`: "Créer votre première inscription de bateau" → "Créer votre premier équipage"
- `boat.noBoats`: "Aucune inscription de bateau" → "Aucun équipage pour le moment"
- `boat.createRegistration`: "Créer une inscription de bateau" → "Créer un équipage"
- `boat.boatInformation`: "Informations du bateau" → "Informations de l'équipage"

#### Admin Section (Simplified)
- `admin.dashboard.totalBoatRegistrations`: "Bateaux inscrits" → "Équipages inscrits"
- `admin.boats.title`: "Toutes les inscriptions de bateaux" → "Tous les équipages"
- `admin.boats.subtitle`: "Voir et gérer les inscriptions de bateaux..." → "Voir et gérer les équipages..."
- `admin.boats.addBoat`: "Ajouter un bateau" → "Ajouter un équipage"
- `admin.boats.totalCount`: "{count} inscriptions de bateaux" → "{count} équipages"
- `admin.boats.editBoat`: "Modifier le bateau" → "Modifier l'équipage"
- `admin.boatRegistrations`: "Gérer les inscriptions d'équipages" → "Gérer les équipages"
- `admin.boatRegistrationsDesc`: "Voir et gérer toutes les inscriptions d'équipages" → "Voir et gérer tous les équipages"

#### Dashboard & Stats (Simplified)
- `dashboard.subtitle`: "Gérez vos inscriptions d'équipage..." → "Gérez vos équipages..."
- `dashboard.stats.boats`: "Total de bateaux" → "Total d'équipages"
- `dashboard.stats.paidBoats`: "Bateaux payés" → "Équipages payés"
- `dashboard.emptyState.description`: "...puis créez des inscriptions de bateaux" → "...puis créez vos équipages"
- `dashboard.actions.manageBoats.title`: "Gérer les bateaux" → "Gérer les équipages"
- `dashboard.actions.manageBoats.description`: "Inscrire et configurer vos inscriptions de bateaux" → "Inscrire et configurer vos équipages"

#### Payment Section (Simplified)
- `payment.boatRegistrations`: "Inscriptions de bateaux" → "Équipages"
- `payment.boatsAvailable`: "{count} bateau disponible" → "{count} équipage disponible"
- `payment.boatsSelected`: "{count} bateau sélectionné" → "{count} équipage sélectionné"

#### Search & Filters (Simplified)
- `boat.filter.search`: "Rechercher par chef de nage, type de bateau..." → "Rechercher par chef de nage, type d'équipage..."
- `boat.searchPlaceholder`: Similar simplification

#### Messages & Confirmations (Simplified)
- All confirmation messages simplified to use "équipage" instead of "inscription de bateau"
- Error messages simplified: "l'inscription de l'équipage" → "l'équipage"

#### Data Export (Simplified)
- `admin.dataExport.exportBoatRegistrations`: "Exporter les inscriptions d'équipages" → "Exporter les équipages"
- `admin.dataExport.standardDescription`: "Exporter les équipiers et les inscriptions d'équipages" → "Exporter les équipiers et les équipages"

#### Timeline & Rules (Simplified)
- `home.timeline.phase1.rule2`: "Créer et supprimer des inscriptions de bateaux" → "Créer et supprimer des équipages"
- Similar simplifications throughout timeline rules

#### Process Steps (Simplified)
- `home.process.step3.title`: "Créez vos inscriptions de bateaux" → "Créez vos équipages"
- `home.process.step3.description`: "...configurez chaque inscription de bateau..." → "...configurez chaque équipage..."

## What Was NOT Changed (Kept as "Boat")

✅ **Physical Boat References:**
- `boat.boatType`: "Boat Type" / "Type de bateau" (refers to physical boat: skiff, four, eight)
- `boat.rentBoat`: "Rent boat from RCPM" / "Louer un bateau du RCPM"
- `boat.rentalInfo`: "Boat rental fees apply" / "Des frais de location de bateau s'appliquent"
- `nav.boatRentals`: "Boat Rentals" / "Location de bateaux"
- `nav.boatInventory`: "Rental Boats" / "Bateaux à louer"
- `admin.boatInventory.*`: All rental boat inventory terms
- `boatRental.*`: All boat rental-related terms
- `boat.types.*`: All boat type translations (skiff, 4-, 4+, 8+, etc.)

## Key Simplifications

### Pattern 1: Remove "Registration/Inscription"
- ❌ "Create Crew Registration" / "Créer une inscription d'équipage"
- ✅ "Create Crew" / "Créer un équipage"

### Pattern 2: Shorten Counts
- ❌ "{count} crew registrations" / "{count} inscriptions d'équipages"
- ✅ "{count} crews" / "{count} équipages"

### Pattern 3: Simplify Actions
- ❌ "Manage Crew Registrations" / "Gérer les inscriptions d'équipages"
- ✅ "Manage Crews" / "Gérer les équipages"

### Pattern 4: Simplify Descriptions
- ❌ "Register and configure your crew entries" / "Inscrire et configurer vos inscriptions d'équipages"
- ✅ "Register and configure your crews" / "Inscrire et configurer vos équipages"

## Files Modified
1. `frontend/src/locales/en.json` - ~60 keys updated and simplified
2. `frontend/src/locales/fr.json` - ~60 keys updated and simplified

## Backend & Database
✅ **No changes made** - All API endpoints, database tables, and backend logic remain unchanged as requested.

## Benefits of Simplification
1. **Shorter, clearer UI text** - Easier to read and understand
2. **More natural language** - Sounds like how people actually speak
3. **Better mobile experience** - Less text to fit on small screens
4. **Consistent terminology** - "Crew" clearly means the team, "Boat" means equipment
5. **Reduced translation complexity** - Simpler phrases are easier to maintain

## Testing Recommendations
1. Navigate through all pages to verify terminology is correct and natural
2. Check navigation menu items (left sidebar) - should say "Crews" not "Crew Registrations"
3. Verify admin pages show simplified terminology
4. Test payment flow - should say "Crews" not "Crew Registrations"
5. Check dashboard statistics labels - should be short and clear
6. Verify search placeholders use simplified language
7. Test confirmation dialogs for natural wording
8. Verify boat rental pages still say "boat" (physical boats)
9. Check mobile view - simplified text should fit better

## Impact
- **User-facing**: All UI text is now shorter, clearer, and more natural
- **Backend**: No impact - all APIs and database remain unchanged
- **Compatibility**: Fully backward compatible - only translation strings changed
- **UX**: Improved readability and reduced cognitive load

## Documentation Updates

The following specification documents have been updated to clearly document the terminology mapping:

### Requirements Document
**File:** `.kiro/specs/impressionnistes-registration-system/requirements.md`

Added a "Terminology Mapping" section in the Glossary that clearly explains:
- Database/API uses "boat" for crew registrations
- UI displays "Crew" (English) / "Équipage" (French) for crew registrations
- "Boat" remains "boat" when referring to physical equipment (boat types, boat rentals)
- Comprehensive mapping table showing the translation between layers

### Design Document
**File:** `.kiro/specs/impressionnistes-registration-system/design.md`

Added a dedicated "Terminology Mapping: Database/API vs UI" section that includes:
- Critical design note explaining the intentional terminology difference
- Clear separation between database/API layer and UI layer terminology
- Detailed mapping table with examples
- Implementation guidelines for developers
- Code examples showing how to handle the terminology in both backend and frontend

### Key Documentation Points

1. **Database/API Layer**: Uses "boat" terminology
   - Database fields: `boat_id`, `boat_type`, `boat_status`
   - API endpoints: `/boats`, `/boats/{boat_id}`
   - Python functions: `create_boat_registration()`, `list_boats()`

2. **UI Layer**: Uses "Crew/Équipage" terminology
   - Display text: "Create Crew", "Manage Crews", "Crew Information"
   - Translation keys: `boat.createRegistration` → "Create Crew"

3. **Physical Equipment**: Uses "Boat" in both layers
   - Boat Type, Boat Rental, Rental Boats

This documentation ensures that:
- Developers understand the terminology mapping when working on the codebase
- The distinction between database/API and UI terminology is clear
- Future maintainers can easily understand why "boat" in code maps to "crew" in UI
- The system maintains consistency while providing user-friendly language


---

# UI Terminology Change: "Team Manager" → "Club Manager" / "Gestionnaire d'équipe" → "Manager de Club"

## Date
December 27, 2025

## Summary
Updated user-facing terminology to use "Club Manager" instead of "Team Manager" for better clarity and alignment with the club-based nature of the registration system.

## Rationale
- "Club Manager" more accurately reflects the role - managing club registrations
- More intuitive for users who are managing their rowing club's entries
- Aligns better with the club-centric nature of the system

## Changes Made

### English Translations (en.json)
Updated all user-facing references from "Team Manager" to "Club Manager":

#### Registration & Authentication
- `auth.register.subtitle`: "Create your team manager account" → "Create your club manager account"

#### Crew Member Management
- `crew.form.clubHint`: "Leave empty to use team manager's club" → "Leave empty to use club manager's club"

#### Admin Section - Crew Members
- `admin.crewMembers.subtitle`: "View and manage crew members for all team managers" → "View and manage crew members for all club managers"
- `admin.crewMembers.searchPlaceholder`: "Search by name, license, or team manager..." → "Search by name, license, or club manager..."
- `admin.crewMembers.filterByTeamManager`: "Filter by Team Manager" → "Filter by Club Manager"
- `admin.crewMembers.allTeamManagers`: "All team managers" → "All club managers"
- `admin.crewMembers.teamManager`: "Team Manager" → "Club Manager"
- `admin.crewMembers.selectTeamManager`: "Team Manager" → "Club Manager"
- `admin.crewMembers.selectTeamManagerPlaceholder`: "Select a team manager..." → "Select a club manager..."

#### Admin Section - Crews
- `admin.boats.subtitle`: "View and manage crews for all team managers" → "View and manage crews for all club managers"
- `admin.boats.searchPlaceholder`: "Search by event, crew type, or team manager..." → "Search by event, crew type, or club manager..."
- `admin.boats.filterByTeamManager`: "Filter by Team Manager" → "Filter by Club Manager"
- `admin.boats.allTeamManagers`: "All team managers" → "All club managers"
- `admin.boats.teamManager`: "Team Manager" → "Club Manager"
- `admin.boats.useTeamManagerInterface`: "To create or edit crews, please use the team manager interface..." → "To create or edit crews, please use the club manager interface..."
- `admin.boats.viewNotAvailable`: "...Team Manager: {teamManager}" → "...Club Manager: {teamManager}"

#### Home Page - Process
- `home.process.intro`: "Team managers register their club and crews..." → "Club managers register their club and crews..."

### French Translations (fr.json)
Updated all user-facing references from "Gestionnaire d'équipe" to "Manager de Club":

#### Registration & Authentication
- `auth.register.subtitle`: "Créez votre compte de gestionnaire d'équipe" → "Créez votre compte de manager de club"

#### Crew Member Management
- `crew.form.clubHint`: "Laissez vide pour utiliser le club du gestionnaire d'équipe" → "Laissez vide pour utiliser le club du manager de club"

#### Admin Section - Crew Members
- `admin.crewMembers.subtitle`: "Voir et gérer les équipiers de tous les gestionnaires d'équipe" → "Voir et gérer les équipiers de tous les managers de club"
- `admin.crewMembers.searchPlaceholder`: "Rechercher par nom, licence ou gestionnaire..." → "Rechercher par nom, licence ou manager..."
- `admin.crewMembers.filterByTeamManager`: "Filtrer par gestionnaire" → "Filtrer par manager"
- `admin.crewMembers.allTeamManagers`: "Tous les gestionnaires" → "Tous les managers"
- `admin.crewMembers.teamManager`: "Gestionnaire d'équipe" → "Manager de Club"
- `admin.crewMembers.selectTeamManager`: "Gestionnaire d'équipe" → "Manager de Club"
- `admin.crewMembers.selectTeamManagerPlaceholder`: "Sélectionner un gestionnaire..." → "Sélectionner un manager..."

#### Admin Section - Crews
- `admin.boats.subtitle`: "Voir et gérer les équipages de tous les gestionnaires d'équipe" → "Voir et gérer les équipages de tous les managers de club"
- `admin.boats.searchPlaceholder`: "Rechercher par épreuve, type d'équipage ou gestionnaire..." → "Rechercher par épreuve, type d'équipage ou manager..."
- `admin.boats.filterByTeamManager`: "Filtrer par gestionnaire" → "Filtrer par manager"
- `admin.boats.allTeamManagers`: "Tous les gestionnaires" → "Tous les managers"
- `admin.boats.teamManager`: "Gestionnaire d'équipe" → "Manager de Club"
- `admin.boats.useTeamManagerInterface`: "...l'interface du gestionnaire d'équipe..." → "...l'interface du manager de club..."
- `admin.boats.viewNotAvailable`: "...Gestionnaire : {teamManager}" → "...Manager : {teamManager}"

#### Home Page - Process
- `home.process.intro`: "Les gestionnaires d'équipe inscrivent leur club..." → "Les managers de club inscrivent leur club..."
- `home.process.step1.description`: "Créez votre compte de gestionnaire..." → "Créez votre compte de manager..."

### Documentation (README.md)
Updated references in the main README:

- Line 15: "...enables rowing club team managers to register..." → "...enables rowing club managers to register..."
- Line 19: "**For Team Managers:**" → "**For Club Managers:**"
- Line 209: "Role-based access control (Team Managers, Admins)" → "Role-based access control (Club Managers, Admins)"

## What Was NOT Changed

### Backend Code & Database
✅ **No changes to backend logic or database:**
- Database field names remain: `team_manager_id`, `PK='TEAM#...'`, etc.
- API parameter names remain: `team_manager_id`
- Python function parameters remain: `team_manager_id`
- DynamoDB partition keys remain: `TEAM#...`

**Rationale:** Changing these would break the entire system. The terminology change is UI-only.

### Backend Comments (Optional)
⚠️ Backend Python file comments and docstrings can optionally be updated for consistency, but this is not critical since they don't affect functionality.

## Files Modified
1. `frontend/src/locales/en.json` - ~20 keys updated
2. `frontend/src/locales/fr.json` - ~20 keys updated
3. `README.md` - 3 references updated
4. `TERMINOLOGY_CHANGES.md` - This documentation

## Key Terminology Mapping

| Layer | English | French |
|-------|---------|--------|
| **UI (User-facing)** | Club Manager | Manager de Club |
| **Database/API** | team_manager_id | team_manager_id |
| **Code Variables** | team_manager_id | team_manager_id |

## Benefits
1. **Clearer role definition** - "Club Manager" is more descriptive than "Team Manager"
2. **Better user understanding** - Users immediately understand they're managing club registrations
3. **Consistent with domain** - Aligns with rowing club terminology
4. **No breaking changes** - Backend remains unchanged, only UI text updated

## Testing Recommendations
1. ✅ Verify registration page shows "Create your club manager account"
2. ✅ Check admin crew members page - filters and labels should say "Club Manager"
3. ✅ Check admin crews page - filters and labels should say "Club Manager"
4. ✅ Verify crew member form hint text references "club manager"
5. ✅ Check home page process section mentions "club managers"
6. ✅ Verify all dropdowns and selects use "Club Manager" / "Manager de Club"
7. ✅ Test search functionality still works (backend uses team_manager_id)
8. ✅ Verify French translations display correctly

## Impact
- **User-facing**: All UI text now uses "Club Manager" terminology
- **Backend**: No impact - all APIs and database remain unchanged
- **Compatibility**: Fully backward compatible - only translation strings changed
- **UX**: Improved clarity and better alignment with user mental model
