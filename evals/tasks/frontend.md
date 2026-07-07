# Frontend Golden Tasks

## Task: accessible-modal
- **Skill:** @react-best-practices
- **Prompt:** Build a React modal dialog component: open/close, focus handling, keyboard support. Show the component code.
- **Rubric:**
  - Focus moves into the modal on open and returns to the trigger on close
  - Escape closes; focus is trapped while open
  - Uses dialog role and aria-modal (or the native dialog element) with a labelled title
  - No scroll-behind; body scroll locked while open

## Task: list-performance
- **Skill:** @react-best-practices
- **Prompt:** A React table of 5,000 rows re-renders fully on every keystroke of its search box. Diagnose and fix; show the code changes.
- **Rubric:**
  - Identifies unstable references or missing memoisation as the re-render cause
  - Applies debouncing to the search input
  - Virtualises the long list or convincingly explains why not
  - Preserves correctness (filtering still matches, keys stable)

## Task: form-validation
- **Skill:** @frontend-dev-guidelines
- **Prompt:** Implement client-side validation for a signup form (email, password, confirm password) with accessible, inline error messages. Show the code.
- **Rubric:**
  - Errors are announced to assistive tech (aria-describedby or live region)
  - Validation runs on blur and on submit, not on every keystroke for untouched fields
  - Password rules stated up front, not only revealed on failure
  - Server-side validation is named as still required
