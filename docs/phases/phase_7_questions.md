# Phase 7 — Facade questions

**Pattern / focus:** Facade.

**Read first:** [Guide 07](../../materials/guides/07-facade.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a video publish pipeline) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the location overview, the facade, and the dashboard Overview page from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

> [!NOTE]
> **_Your Answer_**
>
>Facade provides one simple entry point to a complex system. Without it, every handler would need to call several repositories and services. This creates duplicate code and makes the application harder to maintain.

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

> [!NOTE]
> **_Your Answer_**
>
> A facade should not contain all the business logic. Irrigation rules should stay in the automation strategy, sensor translation should stay in the sensor-related code, and database operations should stay in the repository layer.

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

> [!NOTE]
> **_Your Answer_**
>
> We sgould use Facade when several services and repositories must work together to provide one result. Skip it when one simple repository call is enough. Use Adapter when two interfaces do not match and need to work together.

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

> [!NOTE]
> **_Your Answer_**
>
> The endpoint returns the location name and ID, assigned sensor and actuator counts, and all zones with their thresholds, assigned devices, and latest readings. The readings include tracking status and sampling interval. It also returns the strategy key and the latest recommendation, if available. Readings may come from the sampler or MQTT because both can save readings to the database. The overview uses location_id to show data for the selected location only.

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

> [!NOTE]
> **_Your Answer_**
>
>The required data already exists in the tables created in earlier phases. The facade combines locations, zones, devices, sensor readings, and automation rules into one response. It does not need to store the same information again.

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

> [!NOTE]
> **_Your Answer_**
>
> The handler should have one simple responsibility: receive the request and return the response. The facade handles the coordination of services and repositories. This makes testing easier and allows the query logic to change without changing the HTTP handler.

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

> [!NOTE]
> **_Your Answer_**
>
> Several separate calls could return data from different moments and make the frontend more complicated. One overview request provides a single response for the dashboard. Refresh repeats the same request, so new readings and saved strategies appear without adding more frontend logic.

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

> [!NOTE]
> **_Your Answer_**
>
> Adapter makes an existing interface work with another interface. Facade makes a complex subsystem easier to use through one entry point. In Phase 5, Adapter helps connect interfaces that do not match. In Phase 7, Facade combines greenhouse data for the location overview.

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

> [!NOTE]
> **_Your Answer_**
>
> N+1 happens when the application makes one query to get devices and then another query for each device's latest reading. This creates many database queries. The facade avoids this for overview readings by retrieving the newest readings for all assigned devices in one query using a SQL window function. The existing automation evaluation still performs its own queries.

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

> [!NOTE]
> **_Your Answer_**
>
> Different errors need different solutions. A missing location should return a 404 error, while a database outage is a different problem. Hiding every error makes debugging difficult and can mislead users. The facade should allow errors to be handled clearly instead of treating every problem the same way.
