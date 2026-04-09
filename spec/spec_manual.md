# Software Requirements Specification — MANUAL Pipeline

**Generated**: 2026-04-07T00:43:38.751156 
**Pipeline**: manual
**Total Requirements**: 20
**Functional**: 14  |  **Non-Functional**: 6

---

## Summary

| Metric | Value |
|--------|-------|
| Total Requirements | 20 |
| Functional | 14 |
| Non-Functional | 6 |
| From Goals | 10 |
| From Pain Points | 10 |
| Source Personas | 5 |

---

## Requirements from P1 — Alex the Active User

| Req ID | Type | Priority | Description | Derived From |
|--------|------|----------|-------------|--------------|
| REQ-001 | Functional | High | The system shall support: Log workouts reliably without interruption | goal |
| REQ-002 | Functional | High | The system shall support: Maintain a consistent exercise streak | goal |
| REQ-003 | Non-Functional | High | The system shall address: App crashes frequently during workout logging | pain_point |
| REQ-004 | Non-Functional | High | The system shall address: Loses progress when the app freezes mid-session | pain_point |

## Requirements from P2 — Sam the Syncer

| Req ID | Type | Priority | Description | Derived From |
|--------|------|----------|-------------|--------------|
| REQ-005 | Functional | High | The system shall support: Keep workout data synchronized across all devices | goal |
| REQ-006 | Functional | High | The system shall support: Never lose historical workout data | goal |
| REQ-007 | Functional | High | The system shall address: Sync fails between devices leading to data loss | pain_point |
| REQ-008 | Non-Functional | High | The system shall address: Cloud backup is unreliable or incomplete | pain_point |

## Requirements from P3 — Riley the Runner

| Req ID | Type | Priority | Description | Derived From |
|--------|------|----------|-------------|--------------|
| REQ-009 | Non-Functional | High | The system shall support: Get accurate GPS tracking for outdoor runs | goal |
| REQ-010 | Functional | High | The system shall support: Review precise route maps after each session | goal |
| REQ-011 | Non-Functional | High | The system shall address: GPS tracking is wildly inaccurate | pain_point |
| REQ-012 | Functional | High | The system shall address: Route maps do not match actual paths taken | pain_point |

## Requirements from P4 — Jordan the Social User

| Req ID | Type | Priority | Description | Derived From |
|--------|------|----------|-------------|--------------|
| REQ-013 | Functional | High | The system shall support: Share workouts and achievements with friends | goal |
| REQ-014 | Functional | High | The system shall support: Compete on leaderboards and challenges | goal |
| REQ-015 | Functional | High | The system shall address: Sharing features are difficult to use or broken | pain_point |
| REQ-016 | Functional | High | The system shall address: Leaderboards do not update or display correctly | pain_point |

## Requirements from P5 — Taylor the Budget-Conscious User

| Req ID | Type | Priority | Description | Derived From |
|--------|------|----------|-------------|--------------|
| REQ-017 | Functional | High | The system shall support: Access essential features without a premium subscription | goal |
| REQ-018 | Functional | High | The system shall support: Get clear information about what premium offers | goal |
| REQ-019 | Non-Functional | High | The system shall address: Subscription is too expensive for the value provided | pain_point |
| REQ-020 | Functional | High | The system shall address: Unexpected charges after cancellation | pain_point |

---

## Traceability Matrix

| Req ID | Source Persona | Derived From | Original Text |
|--------|---------------|--------------|---------------|
| REQ-001 | P1 | goal | Log workouts reliably without interruption |
| REQ-002 | P1 | goal | Maintain a consistent exercise streak |
| REQ-003 | P1 | pain_point | App crashes frequently during workout logging |
| REQ-004 | P1 | pain_point | Loses progress when the app freezes mid-session |
| REQ-005 | P2 | goal | Keep workout data synchronized across all devices |
| REQ-006 | P2 | goal | Never lose historical workout data |
| REQ-007 | P2 | pain_point | Sync fails between devices leading to data loss |
| REQ-008 | P2 | pain_point | Cloud backup is unreliable or incomplete |
| REQ-009 | P3 | goal | Get accurate GPS tracking for outdoor runs |
| REQ-010 | P3 | goal | Review precise route maps after each session |
| REQ-011 | P3 | pain_point | GPS tracking is wildly inaccurate |
| REQ-012 | P3 | pain_point | Route maps do not match actual paths taken |
| REQ-013 | P4 | goal | Share workouts and achievements with friends |
| REQ-014 | P4 | goal | Compete on leaderboards and challenges |
| REQ-015 | P4 | pain_point | Sharing features are difficult to use or broken |
| REQ-016 | P4 | pain_point | Leaderboards do not update or display correctly |
| REQ-017 | P5 | goal | Access essential features without a premium subscription |
| REQ-018 | P5 | goal | Get clear information about what premium offers |
| REQ-019 | P5 | pain_point | Subscription is too expensive for the value provided |
| REQ-020 | P5 | pain_point | Unexpected charges after cancellation |
