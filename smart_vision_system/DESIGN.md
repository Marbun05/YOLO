---
name: Smart Vision System
colors:
  surface: '#f8f9fa'
  surface-dim: '#d8dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f5'
  surface-container: '#eceeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#3e4948'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#eff1f2'
  outline: '#6e7979'
  outline-variant: '#bdc9c8'
  surface-tint: '#006a69'
  primary: '#006161'
  on-primary: '#ffffff'
  primary-container: '#0e7c7b'
  on-primary-container: '#c3fffd'
  inverse-primary: '#7cd5d3'
  secondary: '#006d37'
  on-secondary: '#ffffff'
  secondary-container: '#7bf8a1'
  on-secondary-container: '#007239'
  tertiary: '#854524'
  on-tertiary: '#ffffff'
  tertiary-container: '#a35d39'
  on-tertiary-container: '#fff1eb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#98f2f0'
  primary-fixed-dim: '#7cd5d3'
  on-primary-fixed: '#002020'
  on-primary-fixed-variant: '#00504f'
  secondary-fixed: '#7efba4'
  secondary-fixed-dim: '#61de8a'
  on-secondary-fixed: '#00210c'
  on-secondary-fixed-variant: '#005228'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb693'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#713615'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
  surface-tint-cyan: '#E0F2F1'
  surface-bg-soft: '#F5F7F8'
  surface-card: '#FFFFFF'
  indicator-alert-red: '#E74C3C'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 18px
    letterSpacing: 0.5px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.75px
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 1px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1.25rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system powers an intelligent, real-time AI computer vision application for Android. It delivers an interface that balances technological precision with everyday mobile utility. 

The aesthetic is clean, modern Android with subtle tactile depth: crisp elevated surfaces, clear boundary delineations, and fluid feedback loops that foster user trust in machine learning outputs. The system avoids overbearing sci-fi clichés in favor of accessible clarity—allowing bounding boxes, counters, and spatial telemetry to stand out effortlessly against calm, breathable surfaces.

Key brand values include:
- **Clarity & Focus:** Critical detection metrics and live camera viewports command visual focus without noise.
- **Modern Utility:** Native Android ergonomically placed controls optimized for thumb zones and one-handed mobile capture.
- **Algorithmic Trust:** Reassuring green and teal tones communicate reliability, safety, and precision.

## Colors

The palette establishes an authoritative yet welcoming technological presence:

- **Primary Teal (`#0E7C7B`):** Guides user actions, powers primary navigation targets, interactive cards, and highlights vehicle-tracking spatial overlays.
- **Secondary Forest Green (`#27AE60`):** Represents positive state verification, human/person detection tagging, and live status badges.
- **Surface Canvas (`#F5F7F8` to `#E0F2F1`):** Soft, clean daylight canvas that reduces glare and eye fatigue during prolonged use, transitioning smoothly across navigation and status bar tiers.
- **Pure White (`#FFFFFF`):** Reserved for elevated cards, bottom sheets, and floating control overlays over the camera canvas.
- **Indicator Red (`#E74C3C`):** Dedicated exclusively to real-time recording pulses and critical sensor warnings.

## Typography

The system utilizes Inter throughout, capitalizing on its structural neutrality, tall x-height, and superior legibility on mobile screens. 

- **Headlines & Badges:** Utilize bold weights (`700`) to guarantee instant recognition under bright ambient outdoor conditions when using mobile camera modes.
- **Detection Tags & Counters:** Set in uppercase with wide tracking (`0.75px` to `1px`) using `label-sm` and `label-md` for quick peripheral scanning.
- **Body Text:** Uses regular weights (`400`) with generous line-height ratios to ensure log entries, counts, and metadata remain legible across Android viewports.

## Layout & Spacing

Layouts adhere to an 8pt spatial baseline with a responsive single-column fluid mobile grid. 

- **Margin & Safe Areas:** A baseline outer canvas margin of `16px` (`margin-mobile`) expands to `20px` (`margin`) on larger phablet devices. Top boundaries account strictly for system status bars and dynamic camera notches.
- **Card Spacing:** Standard spacing between dashboard card panels is fixed at `space-md` (16px), preventing cognitive clutter while encouraging natural thumb travel.
- **Live Camera Overlays:** Use a decoupled floating overlay system anchored to safe screen insets with `space-md` offsets from physical screen borders.

## Elevation & Depth

Visual hierarchy leverages ambient shadows paired with soft tinted containers to build layered physical structure:

- **Level 0 (Camera & Background Canvas):** The base background utilizes `#F5F7F8` or raw camera feed.
- **Level 1 (Dashboard Cards & App Bar):** Raised using subtle drop shadows tinted with dark slate teal (`rgba(14, 124, 123, 0.08)`) with a blur of 16px and an offset of 4px.
- **Level 2 (Floating Action Panels & Bottom Bars):** Higher physical elevation for control panels over active camera viewports. Employs a diffused shadow (`0 8px 24px rgba(0, 0, 0, 0.12)`) and pure white backdrops to ensure optical isolation from live footage.
- **Level 3 (Detection Overlays & Counter Badges):** Zero blur shadows with sharp 2px high-visibility solid borders (`#0E7C7B` and `#27AE60`) and semi-translucent backplates (`rgba(0, 0, 0, 0.6)`) to preserve legibility against variable environmental backgrounds.

## Shapes

The design system employs a friendly, ergonomic rounded visual language (`roundedness: 2` base):

- **Main Dashboard Cards:** Utilize generous `20px` to `24px` radius (`rounded-xl`), creating inviting touch targets.
- **Floating Overlays & Action Panels:** Feature full top or global corner radii of `20px` to `24px` to blend organically with device corners.
- **Counters, Badges & Action Pills:** Styled as complete pills (`9999px` / `rounded-full`) to immediately designate status and actionable micro-components.
- **Object Bounding Boxes:** Maintain sharp or minimally softened corners (`2px` to `4px`) to preserve geometric fidelity of machine learning bounding vectors.

## Components

### Buttons
- **Primary Action Buttons:** Full-width or capsule buttons in Primary Teal (`#0E7C7B`) with white bold text (`label-lg`), minimum height of `48px` to guarantee thumb ergonomics.
- **Capsule / Pill Buttons:** Pill-shaped interactive tags used for secondary actions (e.g., "LOG DATA TERSIMPAN"), filled with solid primary color or outlined with a 1.5px border.
- **Floating Record Button:** Elevated white surface panel housing a prominent teal camera icon accompanied by an active recording dot in `#E74C3C`.

### Cards & Panels
- **Action Cards:** Pure white `#FFFFFF` cards with `20px` border-radius, `space-lg` inner padding, and soft ambient elevation. Icons are centered or left-aligned within soft teal circular backgrounds (`#E0F2F1`).
- **Floating Camera Action Sheet:** A bottom dock with `24px` top-rounded corners, resting at elevation Level 2 above the live camera preview.

### Badges & Detection HUD
- **Object Bounding Boxes:** 2px solid vector stroke enclosing detected targets (Teal `#0E7C7B` for Vehicles, Green `#27AE60` for Persons).
- **HUD Tag Anchors:** Attached directly to the top edge of each bounding box, displaying uppercase labels with high-contrast text.
- **Floating Counter Pills:** Semi-opaque dark or solid color pills positioned in the top camera viewport, displaying real-time aggregation counters (e.g., `8 KENDARAAN`, `4 ORANG`).

### Lists & Navigation
- **Log Data Items:** White list items with rounded corners (`12px`), separating temporal timestamps from numerical object logs using high-contrast bold counts.
- **Bottom Navigation Bar:** Surface height of `64px`, featuring active indicators in primary teal pills with inactive icons in muted slate gray (`#707979`).