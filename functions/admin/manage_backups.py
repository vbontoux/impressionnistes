"""
Lambda function to manage database backups (create, list, download, delete, restore)
Admin only - routes on API Gateway httpMethod + resource to backup_service handlers.
OPTIONS preflight is handled by API Gateway, not here.
"""
import backup_service
import reset_service
from auth_utils import require_admin, get_user_from_event
from responses import handle_exceptions, error_response

ROUTES = {
    ('POST', '/admin/backups'): backup_service.handle_create,
    ('GET', '/admin/backups'): backup_service.handle_list,
    ('GET', '/admin/backups/{backup_id}/download'): backup_service.handle_download,
    ('DELETE', '/admin/backups/{backup_id}'): backup_service.handle_delete,
    ('POST', '/admin/backups/{backup_id}/restore'): backup_service.handle_restore,
    ('GET', '/admin/reset'): reset_service.handle_counts,
    ('POST', '/admin/reset'): reset_service.handle_reset,
}


@handle_exceptions
@require_admin
def lambda_handler(event, context):
    """Dispatch the request to the matching backup handler"""
    user = get_user_from_event(event)
    handler = ROUTES.get((event.get('httpMethod'), event.get('resource')))
    if handler is None:
        return error_response(404, 'NOT_FOUND', 'Unknown route')
    return handler(event, user)
