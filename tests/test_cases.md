# Manual Test Cases

Use synthetic inputs only. Record observed outcomes in the last three columns during the workshop demonstration.

| Test ID | Feature | Input/Precondition | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| TC-01 | Create valid notice | Submit a valid Lost/Found form | New unique notice is saved and detail page opens after redirect | Pending | Pending | PRG response is a redirect |
| TC-02 | Empty description | Submit form with description blank | Form shows “Description is required.” and stores nothing | Pending | Pending | Server-side validation |
| TC-03 | Invalid category | Send category value not in allowed list | Form rejects it with a clear error | Pending | Pending | Tamper with POST value |
| TC-04 | Long description | Submit description longer than 500 characters | Form rejects it and stores nothing | Pending | Pending | Server checks length |
| TC-05 | Invalid location | Send a location zone outside allowed list | Form rejects it with a clear error | Pending | Pending | |
| TC-06 | Missing notice | Open `/notice/N99999` | Custom 404 page is shown | Pending | Pending | |
| TC-07 | Refresh after create | Submit valid create form, then refresh detail page | Browser refresh repeats GET; no duplicate notice is created | Pending | Pending | Post/Redirect/Get |
| TC-08 | Unknown route | Open `/this-route-does-not-exist` | Custom 404 page; no Flask debug page | Pending | Pending | |
| TC-09 | Resolve notice | POST to resolve an existing Lost/Found notice | Status is saved as Resolved and detail page is shown | Pending | Pending | State change uses POST |
| TC-10 | Resolve twice | Resolve the same notice again | Safe “already resolved” message; no failure | Pending | Pending | |
| TC-11 | Malformed JSON | Use a temporary malformed JSON data file | Generic error page; technical error written to local log; data not overwritten | Pending | Pending | Restore sample JSON afterward |
| TC-12 | XSS-style description | Create description `<script>alert("XSS")</script>` | Script appears as escaped text and does not execute | Pending | Pending | Normal Jinja autoescaping |
