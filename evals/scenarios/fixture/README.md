# Bookings

Room booking service for a small co-working space: create, list, and cancel
bookings, with refunds calculated from how close to the start a guest cancels.

Standard library only, Python 3.11 or later.

```bash
python3 -m unittest discover -s tests
```

Code lives in `bookings/`. The front-desk web app in `web/` is a separate Next.js
project and is out of scope for backend work.
