# Security Notes

This local workshop project uses synthetic lost-and-found notices. It is for learning and should not be exposed as a public service.

1. **POST for changes:** Creating and resolving notices change stored data, so they use POST. GET requests are used to display pages and do not change notice state.
2. **Post/Redirect/Get:** After a successful POST, the server redirects to a GET page. Refreshing that page repeats the GET rather than submitting the create form a second time.
3. **Server-side validation:** Browser checks can be bypassed. The Flask app checks every submitted value before saving.
4. **Allowed values:** Notice type, category, zone, and contact preference must match known choices. This rejects unexpected or tampered form values.
5. **Length limits:** Descriptions are limited to 500 characters so oversized input is not stored or displayed.
6. **Untrusted descriptions:** A description may contain markup or script-like text, so it must be handled as text.
7. **Jinja escaping:** Normal Jinja rendering escapes HTML special characters. A `<script>` string is shown as text instead of being interpreted by the browser. Templates never apply the `safe` filter to descriptions.
8. **Generic error pages:** Stack traces can reveal file paths and implementation details. The browser gets a generic 404 or 500 page; technical details are written to the local log.
9. **Local logs:** Logs support troubleshooting on the workshop machine. The app avoids logging notice descriptions and personal data.
10. **Synthetic data:** Sample notices use fictional descriptions and no real campus or personal records.
11. **No personal contact fields:** The form offers only Campus Helpdesk, Notice Board, or Department Office. It does not collect phone numbers, email addresses, or home addresses.

The application binds to localhost, uses no external database or API, and has no authentication or CSRF protection. Treat it as a local teaching prototype, not a production service.
