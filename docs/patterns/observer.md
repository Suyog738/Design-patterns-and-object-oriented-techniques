# Observer Pattern

## Purpose

When something important happens, the service just **announces it** on the
`EventBus`. It doesn't care who is listening. Listeners (subscribers) decide
what to do, such as saving an alert.

## Who does what

| Role | Class |
|---|---|
| Subject | `EventBus` (`subscribe`, `publish`) |
| Publishers | `ReadingIngest`, `CommandService`, `ActuatorTransitionService` |
| Subscribers | `MoistureThresholdSubscriber`, `AlertPersistenceSubscriber` |

Everything is connected in one place: `composition.py`.

## Events

| Event | Sent when | Result |
|---|---|---|
| `ReadingCreated` | A reading is saved (tracking on only) | Moisture is checked |
| `ThresholdCrossed` | Moisture is below the zone's low | `threshold.crossed` alert (warning) |
| `CommandFailed` | A command is blocked (e.g. max run time) | `command.failed` alert (warning) |
| `ActuatorStateChanged` | An actuator's state changes | `state.changed` alert (critical), only for `error` |

## Example

```text
Reading 0.10 → ReadingIngest → ReadingCreated
  → MoistureThresholdSubscriber → ThresholdCrossed
  → AlertPersistenceSubscriber → alerts table
  → GET /api/alerts → Event feed (polls every 5 s)
```

## Rules

- Publishers **never** save alerts. Only `AlertPersistenceSubscriber` does.
- If one subscriber crashes, the bus logs it and keeps going.
- To add a new reaction (e.g. email), add a subscriber. Don't change the services.

## Observer vs WebSocket (Phase 12)

The `EventBus` only works **inside the backend**. The browser can't hear it,
so for now the UI polls `GET /api/alerts`. In Phase 12, the WebSocket becomes
one more subscriber that pushes events to the browser.