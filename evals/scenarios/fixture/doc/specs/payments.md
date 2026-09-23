# Payments and Refunds Specification

Status: approved by finance on 2026-08-20.

## Refund policy
Refunds depend on how long before the booking start the guest cancels:

| Notice before start | Refund |
|---|---|
| 48 hours or more | 100% of the price |
| 24 to 48 hours | 50% of the price, rounded down to the penny |
| Under 24 hours | nothing |

The thresholds come from the co-working space's published terms (clause 7.2),
so any change needs sign-off from finance, not just engineering.

## Late-cancellation fee (approved, not yet built)
Finance approved a late-cancellation fee on 2026-08-20. A cancellation with
under 24 hours' notice incurs a fee of 500 pence, charged in addition to the lost
refund. Cancellations with 24 hours' notice or more incur no fee.

Implement it as `late_fee_for(booking, now) -> int` in `bookings/payments.py`,
returning the fee in pence. Follow the money rule in
`doc/decisions/2026-08-01-money-in-integer-pence.md`.
