import requests
from odoo import models, fields, api


class WebsiteMonitor(models.Model):
    _name = 'website.monitor'
    _description = 'Website Monitor'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL', required=True)
    port = fields.Integer(string='Port', help="Optional: Used for reference or raw TCP checks.")
    status = fields.Selection([
        ('new', 'New'),
        ('up', 'Up'),
        ('down', 'Down')
    ], string='Status', default='new', tracking=True)
    last_checked = fields.Datetime(string='Last Checked', readonly=True)
    notify_email = fields.Char(string='Notification Email', help="Email to notify on status change")

    def action_check_status_now(self):
        """Manually triggered status check via button."""
        for monitor in self:
            previous_status = monitor.status
            new_status = monitor._check_website_status()

            # Update status and timestamp
            monitor.status = new_status
            monitor.last_checked = fields.Datetime.now()

            # Send email only if status has changed
            if monitor.notify_email and new_status != previous_status:
                monitor._send_email_notification(new_status)

    @api.model
    def check_all_websites(self):
        """Scheduled job to check all monitors periodically."""
        monitors = self.search([])
        for monitor in monitors:
            previous_status = monitor.status
            new_status = monitor._check_website_status()

            monitor.status = new_status
            monitor.last_checked = fields.Datetime.now()

            if monitor.notify_email and new_status != previous_status:
                monitor._send_email_notification(new_status)

    def _check_website_status(self):
        """Check the URL via HTTP GET and return status."""
        try:
            url = self.url.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url  # Default to HTTP

            # Make HTTP GET request
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return 'up'
            else:
                return 'down'
        except Exception:
            return 'down'

    def _send_email_notification(self, status):
        """Send email when monitor status changes."""
        subject = f"[Website Monitor] '{self.name}' status changed to {status.upper()}"
        body = f"""
            <p>Hello,</p>
            <p>The monitor <strong>{self.name}</strong> (<a href="{self.url}">{self.url}</a>)
            has changed status to <strong>{status.upper()}</strong>.</p>
            <p>Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        mail_values = {
            'subject': subject,
            'body_html': body,
            'email_to': ','.join([email.strip() for email in self.notify_email.split(',') if email.strip()]),
            'email_from': self.env.user.email or 'noreply@example.com',
        }
        self.env['mail.mail'].create(mail_values).send()
