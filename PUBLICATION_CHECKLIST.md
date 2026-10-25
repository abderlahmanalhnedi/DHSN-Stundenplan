# Publication checklist / Checkliste

This public repository contains **original source code only**, not timetable exports. The custom integration is experimental and unofficial. **Duale Hochschule Sachsen (DHSN)** and the relevant timetable operator have **not** provided confirmed permission for automated timetable polling. Publication of this source code is not official approval.

- [ ] Ask the university/timetable operator if independent read-only use of the PlanServlet URL is permitted, and whether they impose rate limits or other restrictions.
- [ ] Confirm any applicable conditions around lecturers' names, timetable data and trademarks; stop polling if forbidden.
- [x] No real HAR files, credentials, cookies, tokens, or timetable exports in source control.
- [x] No university logo; no claim of official affiliation.
- [x] English and German installation instructions.
- [x] Initial synthetic offline parser tests.
- [ ] Confirm current Home Assistant compatibility in a clean test environment.
- [ ] Ensure HACS and hassfest CI checks pass.
- [ ] Consider a tagged GitHub Release only after compatibility and operator-policy checks.
- [ ] Consider HACS default catalog only after its additional review requirements are met.

**Do not upload private traces to Issues.**

## Risk-reduction measures / Maßnahmen zur Risikobegrenzung

- [x] Explicitly name Duale Hochschule Sachsen **without presenting this as an official or endorsed product**.
- [x] Document external-request metadata and possible processing of lecturers' names in [PRIVACY.md](PRIVACY.md).
- [x] Provide an operator/rights-holder notice and a route for complaints in [NOTICE.md](NOTICE.md).
- [x] Document that the scheduled requests must be stopped if the operator objects.
- [ ] Obtain written clarification **before announcing a general availability release**.
- [ ] Configure GitHub repository Description and Topics to pass HACS validation; these are GitHub metadata, not files.
