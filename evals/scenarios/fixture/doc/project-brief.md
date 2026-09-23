# Project Brief: Bookings

## What we are building
A booking service for the rooms at a small co-working space. Front-desk staff
create and cancel bookings for guests; guests get refunds on a sliding scale
depending on how early they cancel.

## Scope
- In scope: the Python booking service in `bookings/` and its tests.
- Out of scope: the front-desk web app in `web/` (owned by another team), payments
  provider integration (refund amounts are calculated here, paid out elsewhere).

## Constraints
- Standard library only; no third-party packages without approval.
- Money is always integer pence (see `doc/decisions/`).

## Success criteria
- All tests pass on every PR.
- Refund behaviour matches `doc/specs/payments.md` exactly.
