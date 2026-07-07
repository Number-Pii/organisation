# Writing Golden Tasks

## Task: client-proposal-summary
- **Skill:** @professional-proofreader
- **Prompt:** Write the one-page executive summary of a proposal to rebuild a client's booking system: current pain, proposed approach, timeline, and investment. Audience is the client's managing director.
- **Rubric:**
  - Passes scripts/check_writing.py with zero FAILs (no em/en dashes, no banned phrases)
  - Leads with the client's problem, not the vendor's credentials
  - Concrete claims (numbers, dates, deliverables) rather than adjectives
  - Reads at Flesch 30 to 40 for an executive audience

## Task: incident-postmortem
- **Skill:** @professional-proofreader
- **Prompt:** Draft a blameless postmortem for a 90-minute checkout outage caused by an expired TLS certificate on a payment callback domain. Include timeline, impact, root cause, and actions.
- **Rubric:**
  - Timeline uses absolute times and states detection, mitigation, and resolution separately
  - Root cause names the process gap (no renewal automation/alerting), not a person
  - Every action item has an owner and a date
  - Passes scripts/check_writing.py with zero FAILs

## Task: release-notes
- **Skill:** @professional-proofreader
- **Prompt:** Write customer-facing release notes for a version that adds two features, fixes three bugs, and deprecates one API endpoint (with a migration path). Invent plausible specifics.
- **Rubric:**
  - Deprecation includes the removal date and the migration path
  - Features described by user benefit, not implementation
  - Scannable structure without formulaic repeated openers
  - Passes scripts/check_writing.py with zero FAILs
