# Browser Storage and Email OTP Setup

InterviewIQ's active app stores user profiles and interview history in the user's browser localStorage. The Streamlit app does not use the legacy SQLite module for the personal history dashboard.

## Configure email OTP

Set the following values in local environment variables for development or in **Streamlit Community Cloud → App → Settings → Secrets** for deployment:

~~~toml
SMTP_HOST = "smtp.your-provider.example"
SMTP_PORT = "587"
SMTP_USER = "your-smtp-login"
SMTP_PASSWORD = "your-provider-app-password"
SMTP_FROM = "InterviewIQ <verified-sender@your-domain.example>"
OTP_SIGNING_SECRET = "replace-with-a-long-random-secret"
~~~

Use credentials from a provider that permits transactional email. The sender address should be verified with that provider. Never commit real credentials to Git. The app fails closed if SMTP is not configured; it does not show or bypass OTPs.

## OTP controls

- Six-digit one-time codes.
- Five-minute expiry.
- At most five verification attempts per issued code.
- Minimum 45-second delay between code requests in a Streamlit session.
- Constant-time digest comparison.
- Verified email is associated with the local browser profile.

For production-grade deployment, add provider-level sending quotas, abuse monitoring, and a reverse-proxy or identity provider with stronger request throttling. The in-session throttle is not a global rate limit.

## Browser-only storage limitations

- Data is scoped to the current browser profile/device and does not sync across browsers or devices.
- Clearing site data, private-browsing cleanup, browser policies, or localStorage quota failures may erase or prevent saving data.
- Browser localStorage is not encrypted storage. Scripts executing on the same origin may access it, so do not store secrets or highly sensitive personal information.
- Email verification is performed by the server, but the profile and history are not stored in a server-side user registry. Re-verifying the same email on another device will not restore its local history.
- Export Markdown, HTML, or JSON reports regularly if you need a durable copy. This feature is not a cloud backup.
- Signing out clears the active Streamlit login state but intentionally leaves the local browser profile and history in place on that device.

## Manual deployment smoke test

1. Add the SMTP settings and restart/redeploy the app.
2. Register with an inbox you control and confirm the OTP arrives.
3. Verify an incorrect code, an expired code, and the attempt limit behave as expected.
4. Complete a practice round and refresh the browser; verify the in-progress session is restored.
5. Open **History & Performance** and confirm score trend, rubric, and category graphs appear.
6. Close and reopen the browser using the same profile; verify the local history remains.
7. Test in a different browser/device to confirm history does not sync.
8. Clear the site's local storage only after exporting reports, and confirm the app shows an empty-history state.
