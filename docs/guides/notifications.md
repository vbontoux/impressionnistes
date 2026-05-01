# Notification System Guide

## Overview

The notification system delivers messages to club managers and administrators through multiple channels: email, in-app notifications, and Slack. It handles registration confirmations, issue alerts, deadline reminders, and system events.

**Spec Reference:** NFR-6 (Notification Requirements)

## Notification Channels

| Channel | Recipients | Use Cases |
|---------|-----------|-----------|
| **Email** | Club managers, admins | Confirmations, reminders, flagged issues |
| **In-app** | Club managers, admins | All notifications, accessible via notification center |
| **Slack** | Admins, DevOps | Real-time alerts, system events, payment notifications |

## Notification Types

### Registration Events

| Event | Recipients | Channels |
|-------|-----------|----------|
| New boat registration created | Admin (Slack) | Slack |
| Boat registration completed | Club manager | Email, in-app |
| Boat marked as forfait | Club manager | Email, in-app |

### Payment Events

| Event | Recipients | Channels |
|-------|-----------|----------|
| Payment completed | Club manager | Email, in-app |
| Payment completed | Admin | Slack |
| Payment deadline approaching | Club managers with unpaid boats | Email, in-app |

### Boat Rental Events

| Event | Recipients | Channels |
|-------|-----------|----------|
| Rental request submitted | Admin | Slack |
| Rental confirmed | Club manager | Email, in-app |
| Rental rejected | Club manager | Email, in-app |

### Issue Events

| Event | Recipients | Channels |
|-------|-----------|----------|
| Issue flagged by admin | Club manager | Email, in-app, Slack |
| Issue marked as resolved | Admin | In-app |
| Unresolved issue reminder | Club manager | Email, in-app |

### System Events

| Event | Recipients | Channels |
|-------|-----------|----------|
| System errors | DevOps | Slack |
| Configuration changes | Admin | In-app |
| Contact form submission | Admin | Email, Slack |

## Notification Center

The in-app notification center is accessible from the navigation bar:
- Badge shows count of unread notifications
- Click to open notification list
- Notifications are displayed in reverse chronological order
- Each notification can be marked as read
- Link to the relevant page (crew member, boat, payment) when applicable

## Notification Frequency

For ongoing issues (flagged crew members, unpaid registrations):
- **Immediate:** First notification sent when issue is created
- **Recurring:** Reminders sent at the configured frequency (default: weekly)
- **Deadline:** Additional reminders as registration/payment deadlines approach

The notification frequency is configurable in **Admin → Configuration → Notifications**.

## Language

All notifications are delivered in the recipient's selected language preference (French or English).

## Slack Integration

### Setup

Slack notifications require webhook URLs configured in **Admin → Configuration → Notifications**:
- `slack_webhook_admin` — Admin channel for registration and payment events
- `slack_webhook_devops` — DevOps channel for system events and errors

### Slack Message Format

Slack notifications include:
- Event type and description
- Relevant details (club manager name, boat info, amount, etc.)
- Timestamp
- Link to the admin interface (when applicable)

See [Slack Notifications Guide](./SLACK_NOTIFICATIONS.md) for detailed setup instructions.

## Email Configuration

Emails are sent via AWS SES from the configured sender address (default: `impressionnistes@rcpm-aviron.fr`).

See [Email System Summary](./EMAIL_SYSTEM_SUMMARY.md) for email setup and configuration.

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `notification_frequency_days` | 7 | Days between recurring reminders |
| `session_timeout_minutes` | 30 | Inactivity timeout (triggers logout, not notification) |
| `notification_channels` | email, in_app, slack | Active notification channels |
| `email_from` | impressionnistes@rcpm-aviron.fr | Sender email address |
| `slack_webhook_admin` | (configured by admin) | Slack webhook for admin channel |
| `slack_webhook_devops` | (configured by admin) | Slack webhook for DevOps channel |

## Related Documentation

- [Email System Summary](./EMAIL_SYSTEM_SUMMARY.md) — Email configuration
- [Email Deliverability](./EMAIL_DELIVERABILITY.md) — Email delivery best practices
- [Slack Notifications](./SLACK_NOTIFICATIONS.md) — Slack setup
- [Flagged Issues](./flagged-issues.md) — Issue notification workflow
- [SES Email Setup](./SES_EMAIL_SETUP.md) — AWS SES configuration
