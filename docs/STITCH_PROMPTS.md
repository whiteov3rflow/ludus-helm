# Stitch Prompts Archive

Canonical prompts used to generate the initial UI in [Google Stitch](https://stitch.withgoogle.com/).
Archived here so the design can be regenerated if needed, and so the design intent is
preserved independently of the Stitch tool.

**Source-of-truth for visual rules:** `docs/DESIGN_SYSTEM.md`. These prompts must stay
aligned with that document.

## Usage flow

1. Paste the **Design System prompt** first (establishes baseline)
2. Paste each **screen prompt** one at a time
3. Export as React + TypeScript + Tailwind
4. Drop into `frontend/stitch-exports/` (gitignored), cherry-pick into `frontend/src/pages/`

## Known Stitch quirks

- **Letter-spacing on sidebar tagline:** Stitch repeatedly failed to render
  "training lab manager" on one line with normal letter-spacing; it kept wide-spacing
  and wrapping it as `t r a i n i n g  l a b  m a n a g e r`. Fix by hand post-export
  or drop the tagline entirely.
- **Input theming:** Stitch's first-pass login inputs had white bg on dark card; required
  explicit "dark input" follow-up prompt.
- **Protocol accuracy:** Stitch defaulted to "OpenVPN" on the invite page despite us
  describing WireGuard; explicit correction required.
- **Column completeness:** Stitch dropped the Invite column from the students table on
  first pass; explicit column list in follow-up required.

---

## 1. Design System (paste first)

```
Create a design system for "insec.ml" — a professional security training lab management platform used by instructors to deploy and manage Active Directory CTF labs for students.

Audience: security professionals, penetration testers, and trainees. Not consumer-facing.
Tone: modern, technical, trustworthy. Think Linear × Vercel × HackTheBox. Not cyberpunk, not gamified.

Color palette (dark theme only):
- Background: #0A0B0E
- Surface (cards): #14161C
- Surface elevated: #1C1F28
- Border: #262A36
- Text primary: #E8EAF0
- Text secondary: #8B92A5
- Text muted: #5A6175
- Accent primary (success/ready): #00D4AA (teal-green)
- Accent warning (in-progress): #FFA94D (orange)
- Accent danger (errors/destructive): #FF5E5E (red)
- Accent info (links): #6C8EFF (soft blue)

Typography:
- UI font: Inter (14px default, 24px for page titles, 28px for key numbers)
- Monospace: JetBrains Mono (used for IDs, range names, IP addresses, commands)

Components:
- Border-radius: 12px on cards, 8px on buttons and inputs, 16px on status pills
- Borders: 1px solid, use #262A36
- No heavy shadows; use subtle border + slight elevation via background shift
- Buttons: 40px tall, 14px semibold, primary = teal bg with dark text
- Inputs: 40px tall, dark bg (#1C1F28), focus ring in teal
- Status pills: small (24px tall), soft transparent background of the accent color
- Tables: alternating row backgrounds, hover state lifts bg slightly
- Icons: outline style (Lucide or Heroicons), 20px standard

Logo: text "insec.ml" in Inter Bold with a small teal (#00D4AA) circle dot accent.

Generate all output as React + TypeScript components using Tailwind CSS.
```

## 2. Login

```
Design the Login page for insec.ml (instructor access only).

Layout:
- Full-page dark background (#0A0B0E)
- Centered card: 420px wide, surface #14161C, 12px border-radius, 1px border #262A36, 40px padding
- At top of card: "insec.ml" logo (Inter Bold 28px) with small teal (#00D4AA) dot accent
- Below logo: subtitle "Training lab management" in #8B92A5, 14px
- Form:
  - Email input labeled "Email"
  - Password input labeled "Password"
  - Both inputs 40px tall, bg #1C1F28, border #262A36, focus ring #00D4AA
- Primary button: "Sign in", full-width, 40px tall, bg #00D4AA, text #0A0B0E, 14px semibold
- Below button: "Forgot password?" link in #8B92A5, 13px, centered
- Page footer (bottom of page, not card): "© insec.ml — instructor access only" in #5A6175, 12px

No illustrations, no gradients. Keep it quiet, technical, professional.
```

## 3. Dashboard (Sessions list)

```
Design the main Dashboard page for insec.ml showing a list of training sessions.

Layout:
- Left sidebar (240px wide, bg #14161C, full height):
  - Top: "insec.ml" logo
  - Nav items (vertical list, 40px tall each):
    - Dashboard (active state: bg #1C1F28, left border 2px #00D4AA)
    - Sessions
    - Lab Templates
    - Settings
  - Each nav item has a Lucide icon + label in Inter 14px
  - Bottom of sidebar: user avatar circle + "Instructor" name + small gear icon

- Top bar (56px tall, bg #0A0B0E, border-bottom #262A36):
  - Left: breadcrumb "Dashboard" in #E8EAF0
  - Right: notification bell icon + primary button "+ New session" (teal)

- Main content (32px padding, max-width 1280px):
  - Page title "Sessions" in Inter 24px Bold
  - Subtitle "Manage your training lab deployments" in #8B92A5

  - Stats row: 4 cards in a row, each with surface #14161C, 20px padding, 12px radius:
    - "Active sessions" — big number 28px bold + teal indicator
    - "Total students" — big number + info blue indicator
    - "Provisioned labs" — big number + teal indicator
    - "Errors" — big number + red indicator if >0, otherwise muted

  - "Recent sessions" table:
    - Section header "Recent sessions" + search input on the right
    - Columns: Name | Lab template | Mode | Students | Status | Start date | Actions
    - Row bg alternating #14161C / transparent, hover lifts to #1C1F28
    - Mode column: small pill "Dedicated" (info blue) or "Shared" (muted gray)
    - Status column pills:
      * Active: teal bg rgba(0,212,170,0.15), text #00D4AA
      * Provisioning: orange bg rgba(255,169,77,0.15), text #FFA94D
      * Draft: bg #262A36, text #8B92A5
      * Ended: transparent, text #5A6175
    - Range IDs shown in JetBrains Mono
    - Actions column: three-dot vertical menu icon

  - Empty state variant: center content with subtle icon + "No sessions yet" heading + "Create your first training session" button

Use Inter for UI, JetBrains Mono for any IDs/names, Lucide for icons.
```

## 4. Session Detail

```
Design the Session Detail page for insec.ml — shows one training session with its students and controls.

Layout:
- Same sidebar + top bar as Dashboard
- Top bar breadcrumb: "Sessions > AD Attacks Workshop - April 2026"

- Header section:
  - Row 1: Session name "AD Attacks Workshop - April 2026" (24px bold) + status pill "Active" (teal)
  - Row 2: Description in #8B92A5 "Hands-on AD exploitation training for 12 students"
  - Row 3 (right-aligned action row):
    - "Provision all" primary button (teal)
    - "Reset all" secondary outlined button
    - "End session" danger button (red outline, red text)

- Info cards row (3 cards, equal width):
  Card 1 — "Lab template": Label + value + "View details →" link
  Card 2 — "Mode": Label + pill "Dedicated" or "Shared" + sub-text
  Card 3 — "Dates": Label + value in JetBrains Mono

- Students section:
  - Header "Students (12)" + "Import CSV" button + "Add student" primary button
  - Table columns: [checkbox] | Name | UserID | Range ID | Status | Invite | Actions
  - UserID in JetBrains Mono, short format ("CK", "SN", "AC")
  - Range ID in JetBrains Mono
  - Status pills: Ready (teal), Pending (gray), Provisioning (orange + spinner), Error (red + alert icon)
  - Invite column: Copy-link icon button + redemption indicator (green dot "Redeemed" or gray clock "Pending")
  - Actions: three-dot menu
  - Floating bulk action bar when rows selected: "N selected" + "Reset selected" + "Remove selected"

- Collapsible "Activity log (N)" section at bottom:
  - Expanded: timeline with JetBrains Mono timestamps + action descriptions
  - Example: "14:22:11  Provisioned CK → range GOADLight3c1abb"
```

## 5. Public Invite

```
Design the public Invite page for insec.ml — where a student lands after receiving their invite link, and downloads their WireGuard VPN config.

This page is public (no login), reached via /invite/{token}.

Layout:
- Full-page dark background (#0A0B0E), no sidebar, no top nav
- Centered card, 520px wide, surface #14161C, 12px radius, 1px border #262A36, 40px padding
- Inside card:
  - Small "insec.ml" logo at top with teal dot
  - Heading: "Welcome, Senou Azuma"
  - Subheading: "Your lab is ready to connect." in #8B92A5

  - Info block (inset, bg #1C1F28, 16px padding, 8px radius):
    - "Training": "AD Attacks Workshop"
    - "Lab": "GOADLight Active Directory"
    - "Entry point": "THOUSAND-SUNNY" + IP "10.3.10.21" in JetBrains Mono
    - "Expires": "Apr 22, 2026 - 23:59 UTC" in JetBrains Mono

  - "Get connected" section with numbered steps:
    1. Download the WireGuard config below
    2. Import into WireGuard client
    3. Activate tunnel, then ping the entry point to verify

  - Big primary button: "Download VPN config"
    - Full-width, 48px tall, bg #00D4AA, text #0A0B0E
    - Download arrow icon on left

  - Small muted text below button: "File: senou.conf · Contains your private key"

  - Row of 5 platform icons (Windows, macOS, Linux, iOS, Android), each linking to the WireGuard client download page for that platform

  - Collapsible "Having issues?" at bottom with troubleshooting tips

- Page footer: "POWERED BY INSEC.ML" in #5A6175
```

---

## Iteration notes (from initial run)

**Round 1 issues → follow-up prompts applied:**

1. Login inputs were white/light → sent dark-theming correction
2. Stray "Instructor Access Verification" divider → removed
3. "OpenVPN" instead of WireGuard → corrected
4. Students table missing Invite column → added
5. Bulk action bar missing → added
6. Activity log missing → added
7. Student UserIDs formatted as `usr_98f2a1` → changed to short caps (CK, SN)
8. "SECURITY OPS" sidebar tagline → replaced with "training lab manager"

**Round 2 unresolved:**

- Sidebar tagline letter-spacing bug persists — fix manually in code export,
  do not re-prompt Stitch (it's a consistent failure mode).
