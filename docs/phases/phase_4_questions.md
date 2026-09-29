# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

> [!NOTE]
> **_Your Answer_**
>
> The Builder creates a complex object step by step and checks that it is valid at the end. This prevents incomplete or invalid data from being saved.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

> [!NOTE]
> **_Your Answer_**
>
> The product is LocationConfig, the builder is LocationConfigBuilder, the director is optional, and the client uses the builder. Before build() succeeds, it is not a finished valid product.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

> [!NOTE]
> **_Your Answer_**
>
> It should reject an empty location name, no zones, empty zone names, and invalid moisture thresholds. These rules belong in the domain builder so they apply everywhere, not only through the API.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

> [!NOTE]
> **_Your Answer_**
>
> The builder produces a location with its zones. We use location_id because the application is based on locations and zones. We do not use greenhouse_id.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

> [!NOTE]
> **_Your Answer_**
>
> The API receives a DTO, the builder creates and validates the configuration, and the repository saves it. If build() fails, nothing should be saved. A device needs an existing zone, so the client only sends the zone_id.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

> [!NOTE]
> **_Your Answer_**
>
> If the location is saved but a zone fails, we could get incomplete data. One transaction makes sure everything is saved together or nothing is saved.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

> [!NOTE]
> **_Your Answer_**
>
> The wizard collects the data and sends it to the API. The Builder handles the actual validation, keeping business rules out of React.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

> [!NOTE]
> **_Your Answer_**
>
> Factory Method answers “which type?”. Abstract Factory answers “which matching set?”. Builder answers “how do we build one valid object step by step?”

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

> [!NOTE]
> **_Your Answer_**
>
> Fluent chaining is just a coding style. Builder is a design pattern for step-by-step construction and validation of a complex object.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

> [!NOTE]
> **_Your Answer_**
>
> Only validating in FastAPI is risky because other code could create invalid data. Changing the product after build() is also wrong because the final LocationConfig should be immutable.
