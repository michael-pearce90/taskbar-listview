# Module Admission

TechTools for Windows modules should be accepted only when they have a narrow
purpose, a clear safety boundary, and a support model that can be tested.

## Admission Criteria

- The module has a technician-focused use case.
- The module is opt-in.
- The module has a documented rollback path.
- The module avoids broad system modification.
- The module names data it reads, writes, or logs.
- The module has clear non-goals.
- The module can be tested without claiming unsupported compatibility.
- The module preserves GPLv3 and third-party attribution obligations.

## Required Before Code

Before implementation code is added, a module should have:

- a module README;
- a status statement;
- safety and privacy boundaries;
- non-goals;
- proposed verification evidence;
- support criteria; and
- licensing or attribution notes.

Browser Choice Tools currently satisfies only the proposal placeholder step.
It is not admitted for implementation work by this documentation change.
