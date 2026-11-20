"""
Reset service: selective purge of operational data (single source of truth).

Defines the purge sets, their key rules, the dependency rules, classification,
closure and item counts. Reuses backup_service (scan, batch write, backup, audit).

Values mirrored in frontend/src/utils/resetRules.js: set ids, DEPENDENCIES and
CONFIRMATION_PHRASE. Keep both sides identical.

Protected data (CONFIG, RACE, CLUB, AUDIT#DATABASE_BACKUP) is never listed in a
rule, so it can never be classified nor purged.
"""
import logging
import os
import time
from typing import Any, Dict, Iterable, Optional, Set, Tuple

import boto3

import backup_service
from responses import parse_request_body, success_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONFIRMATION_PHRASE = "PURGER LA BASE"
ADMINS_GROUP = "admins"

# id -> label and key rules. A rule is (PK pattern, SK pattern);
# a trailing "*" means prefix match, otherwise exact match.
PURGE_SETS: Dict[str, Dict[str, Any]] = {
    "boats": {"label": "Équipages", "rules": [("TEAM#*", "BOAT#*")]},
    "payments": {"label": "Paiements", "rules": [("TEAM#*", "PAYMENT#*")]},
    "crew": {"label": "Équipiers", "rules": [("TEAM#*", "CREW#*")]},
    "managers": {
        "label": "Team managers",
        "rules": [("USER#*", "PROFILE"), ("USER#*", "CONSENT#*")],
    },
    "temp_access": {"label": "Accès temporaires", "rules": [("TEMP_ACCESS", "USER#*")]},
    "audit_logs": {
        "label": "Journaux d'audit",
        "rules": [(pk, "*") for pk in (
            "AUDIT#PERMISSION_BYPASS",
            "AUDIT#PERMISSION_DENIAL",
            "AUDIT#PERMISSION_CONFIG",
            "AUDIT#TEMP_ACCESS_GRANT",
            "AUDIT#TEMP_ACCESS_REVOKE",
        )],
    },
}

# Deletion order: dependents first
PURGE_ORDER = ("payments", "boats", "crew", "temp_access", "managers", "audit_logs")

# Purging a key set also requires purging its values. Already transitive,
# so the closure is a single union.
DEPENDENCIES: Dict[str, Set[str]] = {
    "boats": {"payments"},
    "crew": {"boats", "payments"},
    "managers": {"boats", "payments", "crew", "temp_access"},
}


# ---------------------------------------------------------------------------
# Errors (mapped by backup_service._run to error_response)
# ---------------------------------------------------------------------------
class InvalidSelection(backup_service.BackupError):
    """Unknown ids, empty selection, or selection not closed under DEPENDENCIES"""
    code, status = "INVALID_SELECTION", 400


class BackupRequired(backup_service.BackupError):
    """Production purge requested without the Pre_Reset_Backup"""
    code, status = "BACKUP_REQUIRED", 400


class PreResetBackupFailed(backup_service.BackupError):
    """The Pre_Reset_Backup failed: nothing was deleted"""
    code, status = "PRE_RESET_BACKUP_FAILED", 500


class ResetPartial(backup_service.BackupError):
    """The purge failed after some deletions"""
    code, status = "RESET_PARTIAL", 500


# InvalidConfirmation is reused from backup_service
InvalidConfirmation = backup_service.InvalidConfirmation


# ---------------------------------------------------------------------------
# Classification, closure, counts
# ---------------------------------------------------------------------------
def _matches(pattern: str, value: str) -> bool:
    """Trailing '*' = prefix match; otherwise exact match"""
    if pattern.endswith("*"):
        return value.startswith(pattern[:-1])
    return value == pattern


def classify(pk: str, sk: str) -> Optional[str]:
    """
    Return the id of the purge set owning the key, or None.

    None for Protected_Data and for keys that match no rule (they are kept).
    """
    pk, sk = str(pk or ""), str(sk or "")
    for set_id, definition in PURGE_SETS.items():
        for pk_pattern, sk_pattern in definition["rules"]:
            if _matches(pk_pattern, pk) and _matches(sk_pattern, sk):
                return set_id
    return None


def resolve_closure(ids: Iterable[str]) -> Set[str]:
    """The ids plus everything their Dependency_Rules require"""
    closed: Set[str] = set()
    for set_id in ids:
        closed.add(set_id)
        closed |= DEPENDENCIES.get(set_id, set())
    return closed


def _key_of(item: Dict[str, Any]) -> Tuple[str, str]:
    """(PK, SK) string values of a typed item ('' when absent)"""
    return (item.get("PK", {}).get("S", ""), item.get("SK", {}).get("S", ""))


def compute_item_counts() -> Tuple[Dict[str, int], int]:
    """
    Count the items of every purge set with ONE table scan.

    Returns:
        (counts with all six set ids, cognito_accounts_max), where
        cognito_accounts_max is the number of USER#<sub> / PROFILE items.
    """
    counts = {set_id: 0 for set_id in PURGE_SETS}
    cognito_accounts_max = 0
    for item in backup_service.scan_table():
        pk, sk = _key_of(item)
        set_id = classify(pk, sk)
        if set_id is None:
            continue
        counts[set_id] += 1
        if set_id == "managers" and sk == "PROFILE":
            cognito_accounts_max += 1
    return counts, cognito_accounts_max


# ---------------------------------------------------------------------------
# Request validation (task 2.4)
# ---------------------------------------------------------------------------
def validate_request(body: Any) -> Tuple[Set[str], bool, bool]:
    """
    Validate a purge request. Nothing is read from or written to the database.

    Order: phrase, selection, Cognito flag, backup rule. The selection must
    already be closed under DEPENDENCIES (the closure is never applied here).
    The environment comes from ENVIRONMENT, never from the request.

    Returns:
        (sets, delete_cognito, backup_before)

    Raises:
        InvalidConfirmation, InvalidSelection, BackupRequired
    """
    if not isinstance(body, dict):
        raise InvalidConfirmation("The confirmation phrase is missing or invalid")

    # 1. Phrase (exact, case-sensitive)
    phrase = body.get("confirmation_phrase")
    if not isinstance(phrase, str) or phrase != CONFIRMATION_PHRASE:
        raise InvalidConfirmation(
            f"The confirmation phrase must be exactly '{CONFIRMATION_PHRASE}'")

    # 2. Selection
    raw_sets = body.get("sets")
    if not isinstance(raw_sets, list) or not raw_sets:
        raise InvalidSelection("'sets' must be a non-empty list of purge set ids")
    if not all(isinstance(s, str) for s in raw_sets):
        raise InvalidSelection("'sets' must contain only strings")
    selection = set(raw_sets)

    unknown = sorted(selection - set(PURGE_SETS))
    if unknown:
        raise InvalidSelection("Unknown purge set(s)", {"unknown": unknown})

    missing = sorted(resolve_closure(selection) - selection)
    if missing:
        raise InvalidSelection(
            "The selection is not closed under the dependency rules",
            {"missing": missing})

    # 3. Cognito flag
    delete_cognito = body.get("delete_cognito", False)
    if not isinstance(delete_cognito, bool):
        raise InvalidSelection("'delete_cognito' must be a boolean")
    if delete_cognito and "managers" not in selection:
        raise InvalidSelection(
            "'delete_cognito' requires the 'managers' set", {"missing": ["managers"]})

    # 4. Backup rule (a missing field means true)
    backup_before = body.get("backup_before", True)
    if not isinstance(backup_before, bool):
        raise InvalidSelection("'backup_before' must be a boolean")
    if os.environ.get("ENVIRONMENT") == "prod" and backup_before is False:
        raise BackupRequired("The Pre_Reset_Backup is mandatory in production")

    return selection, delete_cognito, backup_before


# ---------------------------------------------------------------------------
# Execution (task 2.6)
# ---------------------------------------------------------------------------
def _empty_cognito_result(requested: bool = False) -> Dict[str, Any]:
    return {"requested": requested, "deleted": 0, "skipped_admins": 0,
            "not_found": 0, "failed": []}


def _pre_reset_backup(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Take the Pre_Reset_Backup; any failure aborts the purge (nothing deleted)"""
    try:
        return backup_service.create_backup(backup_service.CATEGORY_RESET, user)
    except backup_service.BackupError as e:
        details = {"failed_artifact": e.details.get("failed_artifact"),
                   "database_modified": False}
        if e.details.get("backup_id"):
            details["backup_id"] = e.details["backup_id"]
        raise PreResetBackupFailed("The pre-reset backup failed: nothing was deleted",
                                   details)
    except Exception as e:
        logger.error(f"Pre-reset backup failed: {e}", exc_info=True)
        raise PreResetBackupFailed("The pre-reset backup failed: nothing was deleted",
                                   {"database_modified": False})


def _keys_by_set(selected: Set[str]) -> Tuple[Dict[str, list], list]:
    """One scan: typed keys of the selected sets, and the managers' subs"""
    keys: Dict[str, list] = {set_id: [] for set_id in selected}
    subs: list = []
    for item in backup_service.scan_table():
        pk, sk = _key_of(item)
        set_id = classify(pk, sk)
        if set_id not in selected:
            continue
        keys[set_id].append({"PK": {"S": pk}, "SK": {"S": sk}})
        if set_id == "managers" and sk == "PROFILE" and pk.startswith("USER#"):
            subs.append(pk[len("USER#"):])
    return keys, subs


def _delete_keys(keys: list) -> Iterable[int]:
    """Delete keys in chunks of 25; yield the size of each successful chunk"""
    table_name = backup_service._get_table_name()
    size = backup_service.BATCH_SIZE
    for start in range(0, len(keys), size):
        chunk = keys[start:start + size]
        backup_service.batch_write_with_retry(
            {table_name: [{"DeleteRequest": {"Key": key}} for key in chunk]})
        yield len(chunk)


def _audit(user, outcome, selected, deleted, delete_cognito, cognito, backup_id,
           backup_taken) -> bool:
    return backup_service.write_audit("reset_database", user, {
        "outcome": outcome,
        "sets": [s for s in PURGE_ORDER if s in selected],
        "deleted": dict(deleted),
        "delete_cognito": delete_cognito,
        "cognito_deleted": cognito["deleted"],
        "cognito_failed": len(cognito["failed"]),
        "backup_taken": backup_taken,
        "pre_reset_backup_id": backup_id,
        "environment": os.environ.get("ENVIRONMENT"),
    })


def execute_reset(body: Any, user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Purge the selected sets. Used by the Lambda and the CLI.

    Returns the PurgeResult: sets, deleted, total_deleted, cognito,
    pre_reset_backup (or None), audit_written, duration_ms.

    Raises:
        InvalidConfirmation, InvalidSelection, BackupRequired: nothing done
        PreResetBackupFailed: nothing deleted (database_modified false)
        BackupError (INTERNAL_ERROR): failure before deletion, nothing deleted
        ResetPartial: failure during deletion (details: stage, deleted,
            pre_reset_backup_id, cognito)
    """
    started = time.monotonic()
    selected, delete_cognito, backup_before = validate_request(body)

    backup: Optional[Dict[str, Any]] = None
    if backup_before or os.environ.get("ENVIRONMENT") == "prod":
        backup = _pre_reset_backup(user)
    backup_id = backup["backup_id"] if backup else None

    try:
        keys, subs = _keys_by_set(selected)
    except Exception as e:
        logger.error(f"Reset scan failed: {e}", exc_info=True)
        raise backup_service.BackupError(
            "The purge could not start: nothing was deleted",
            {"database_modified": False, "pre_reset_backup_id": backup_id})

    deleted: Dict[str, int] = {s: 0 for s in PURGE_ORDER if s in selected}
    cognito = _empty_cognito_result(delete_cognito)

    stage = None
    try:
        for set_id in deleted:
            stage = set_id
            for count in _delete_keys(keys[set_id]):
                deleted[set_id] += count
    except Exception as e:
        logger.error(f"Reset failed while deleting '{stage}': {e}", exc_info=True)
        _audit(user, "partial", selected, deleted, delete_cognito, cognito,
               backup_id, backup is not None)
        raise ResetPartial(
            "The purge failed before completion",
            {"stage": stage, "deleted": dict(deleted),
             "pre_reset_backup_id": backup_id, "cognito": "not_attempted"})

    # Cognito step (task 2.8): only after every DynamoDB deletion succeeded
    if delete_cognito:
        cognito = _cognito_step(subs)

    audit_written = _audit(user, "success", selected, deleted, delete_cognito,
                           cognito, backup_id, backup is not None)

    return {
        "sets": list(deleted),
        "deleted": deleted,
        "total_deleted": sum(deleted.values()),
        "cognito": cognito,
        "pre_reset_backup": ({"backup_id": backup["backup_id"],
                              "native_backup": backup.get("native_backup")}
                             if backup else None),
        "audit_written": audit_written,
        "duration_ms": int((time.monotonic() - started) * 1000),
    }


# ---------------------------------------------------------------------------
# Cognito step (task 2.8)
# ---------------------------------------------------------------------------
_cognito_client = None


def _get_cognito_client():
    """Lazy cognito-idp client (tests reset it so it is built inside the mock)"""
    global _cognito_client
    if _cognito_client is None:
        _cognito_client = boto3.client('cognito-idp')
    return _cognito_client


def _error_code(error: Exception) -> str:
    response = getattr(error, "response", None)
    if isinstance(response, dict):
        return response.get("Error", {}).get("Code") or type(error).__name__
    return type(error).__name__


def delete_cognito_accounts(subs: Iterable[str]) -> Dict[str, Any]:
    """
    Delete the Cognito accounts of the purged team managers (Username = sub).

    Per account: AdminListGroupsForUser; members of `admins` are skipped; a
    failed group check skips the account and reports it (fail closed); then
    AdminDeleteUser. UserNotFoundException counts as not_found; any other error
    is recorded in `failed` and the loop continues. Never raises.
    """
    subs = list(subs)
    result = _empty_cognito_result(True)
    result["requested"] = True

    try:
        pool_id = os.environ["USER_POOL_ID"]
        client = _get_cognito_client()
    except Exception as e:
        logger.error(f"Cognito step could not start: {e}", exc_info=True)
        result["failed"] = [{"sub": sub, "code": "CognitoUnavailable"} for sub in subs]
        return result

    for sub in subs:
        try:
            groups = client.admin_list_groups_for_user(UserPoolId=pool_id, Username=sub)
            names = {g.get("GroupName") for g in groups.get("Groups", [])}
            # Paginated answers: keep reading so an admin is never missed
            while groups.get("NextToken"):
                groups = client.admin_list_groups_for_user(
                    UserPoolId=pool_id, Username=sub, NextToken=groups["NextToken"])
                names |= {g.get("GroupName") for g in groups.get("Groups", [])}
        except Exception as e:
            code = _error_code(e)
            if code == "UserNotFoundException":
                result["not_found"] += 1
            else:
                logger.error(f"Cognito group check failed for {sub}: {code}")
                result["failed"].append({"sub": sub, "code": code})
            continue

        if ADMINS_GROUP in names:
            result["skipped_admins"] += 1
            continue

        try:
            client.admin_delete_user(UserPoolId=pool_id, Username=sub)
            result["deleted"] += 1
        except Exception as e:
            code = _error_code(e)
            if code == "UserNotFoundException":
                result["not_found"] += 1
            else:
                logger.error(f"Cognito deletion failed for {sub}: {code}")
                result["failed"].append({"sub": sub, "code": code})

    return result


def _cognito_step(subs: list) -> Dict[str, Any]:
    return delete_cognito_accounts(subs)


# ---------------------------------------------------------------------------
# API adapters (task 2.10)
# ---------------------------------------------------------------------------
def handle_counts(event: Dict[str, Any], user: Optional[Dict[str, Any]]):
    """GET /admin/reset: item counts per purge set and environment flags"""
    def action():
        environment = os.environ.get("ENVIRONMENT", "")
        counts, cognito_accounts_max = compute_item_counts()
        return success_response({
            "environment": environment,
            "backup_required": environment == "prod",
            "counts": counts,
            "cognito_accounts_max": cognito_accounts_max,
        })
    return backup_service._run(action)


def handle_reset(event: Dict[str, Any], user: Optional[Dict[str, Any]]):
    """POST /admin/reset: purge the selected sets (missing/invalid JSON = 400)"""
    def action():
        try:
            body = parse_request_body(event)
        except ValueError:
            body = None
        if not isinstance(body, dict):
            raise backup_service.InvalidConfirmation(
                "The request body is missing or is not a valid JSON object")
        return success_response(execute_reset(body, user))
    return backup_service._run(action)
