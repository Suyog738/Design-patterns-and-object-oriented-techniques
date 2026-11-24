# Phase 11 — Observer questions

**Pattern / focus:** Observer.

**Read first:** [Guide 11](../../materials/guides/11-observer.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example live auction bids) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the event bus, alerts, publishers, and the event feed from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Observer in plain language. What is a **one-to-many** dependency here, and why must the subject notify dependents **without** knowing their concrete classes?

> [!NOTE]
> **_Your Answer_**
>
> When something happens, the bus tells everyone who is listening. One event can reach many listeners. The bus doesn't know who they are, so we can add new listeners without changing the publisher.

2. Name the participants (**subject / event bus**, **observer / subscriber**, **concrete observers**, **event**, **publisher**). What does `subscribe` / `unsubscribe` / `publish` (or `notify`) each do? This example’s `EventBus` implements `subscribe` and `publish` only.

> [!NOTE]
> **_Your Answer_**
>
> - Subject: EventBus
> - Publishers: ReadingIngest, CommandService, ActuatorTransitionService
> - Subscribers: MoistureThresholdSubscriber, AlertPersistenceSubscriber
> - Events: ReadingCreated, ThresholdCrossed, CommandFailed, ActuatorStateChanged
> subscribe registers a listener, publish calls all listeners for that event, and unsubscribe removes a listener (we don't use it).
3. When should you use Observer, and when should you skip it (only one listener forever; or you need a strict multi-step workflow with guaranteed order)?

> [!NOTE]
> **_Your Answer_**
>
> Use it when several parts of the app need to react to the same event. Skip it when there's only one listener, or when the steps must happen in a fixed order.

## B. This phase of the application

4. Give at least two **domain events** you publish in this lab, including `reading.created` (only when `tracking_enabled` is true), a threshold-crossed event, command-failed, and `ActuatorStateChanged`. The persistence subscriber stores `state.changed` only when that state is `error`. Who publishes `reading.created`, and why do a manual read, the simulation sampler, and MQTT translation share that one ingest publish? Why must a publisher **not** import the alerts repository or the UI?

> [!NOTE]
> **_Your Answer_**
>
> Examples are ReadingCreated (only if tracking is on), ThresholdCrossed, CommandFailed and ActuatorStateChanged. ReadingIngest publishes readings, and every reading source goes through it, so there's one publish point. Publishers don't import alerts or UI code, so they stay simple.

5. What does `AlertPersistenceSubscriber` (or your equivalent) do when it handles an event? Name the three stored rows: `threshold.crossed` / `warning` / `Moisture below zone low`, `command.failed` / `warning` / the failure message, and `state.changed` / `critical` / `Actuator entered error`. Why do alerts live in the `alerts` table so the event feed still shows them after a **refresh**?

> [!NOTE]
> **_Your Answer_**
>
> It saves an alert row:

> - threshold.crossed / warning / "Moisture below zone low"
> - command.failed / warning / failure message
> - state.changed / critical / "Actuator entered error"
> Saving to the database means the alerts are still there after a refresh.

6. The dashboard Event feed **polls** `GET /api/alerts` every 5 seconds in this phase. `services/realtime.ts` is only a **stub**. Why is full WebSocket **not** required in this phase? What should Phase 12 plug into so you do **not** re-implement pub/sub inside socket handlers? Phase 12 subscribes a dashboard socket to this same bus, and the example publishes `AlertCreated` after each insert for that socket.

> [!NOTE]
> **_Your Answer_**
>
> Polling is enough for this phase. In Phase 12, the WebSocket just becomes another subscriber on the same bus, so there's nothing to rebuild.

7. Describe the must-demo path: a **tracked** low-moisture reading leads to an alert row that appears in the feed after poll. Which objects collaborate (reading pipeline → bus → subscriber → API → UI), and which object must **not** write the alert directly? What is stored, and what is not published, when `tracking_enabled` is false?

> [!NOTE]
> **_Your Answer_**
>
> Reading 0.10 → ReadingIngest → ReadingCreated → moisture subscriber → ThresholdCrossed → alert subscriber saves the row → GET /api/alerts → Event feed. ReadingIngest must not save the alert itself. With tracking off, the reading is saved but no event is sent.

## C. Compare, contrast, and scenarios

8. Contrast Observer with **Facade**. Facade simplifies **calling into** a subsystem. Observer **fans out** notifications after something happened. How do both appear in this greenhouse (Phase 7 overview vs this phase)?

> [!NOTE]
> **_Your Answer_**
>
> Facade makes it easy to ask for something, like the Phase 7 overview. Observer tells listeners when something happened, like the Phase 11 alerts.


9. Contrast Observer with **Command**. Command captures **intent to act**. Observer propagates **outcomes**. How can `execute()` publish an event without the command class knowing who persists alerts?

> [!NOTE]
> **_Your Answer_**
>
> Command does the action. Observer shares the result. CommandService publishes CommandFailed to the bus without knowing who saves the alert.



10. One subscriber throws during `notify` / `publish` and aborts the loop, so later subscribers never run. Why is that a trap? What should the bus do so a failing alert writer does not block metrics (or later WebSocket) subscribers?

> [!NOTE]
> **_Your Answer_**
>
> If one listener crashes, the others never run. Our bus catches each error and keeps going, so one broken listener doesn't stop the rest.
