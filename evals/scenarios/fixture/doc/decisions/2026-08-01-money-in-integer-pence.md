# Decision: money is stored and calculated as integer pence

Date: 2026-08-01

## Context
Early prototypes used floats for prices and produced refunds like 1499.9999.

## Decision
Every amount of money in the codebase is an `int` number of pence. Percentages
are applied with integer arithmetic and rounded down (`price * percent // 100`).
Never use `float` or `Decimal` for money in this service.

## Consequences
Display code converts pence to pounds at the edge. Tests assert exact integers.
