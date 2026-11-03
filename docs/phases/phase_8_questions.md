# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

> [!NOTE]
> ***Your Answer***
>
> The State pattern allows an object to behave differently depending on its current state. It avoids using too many boolean flags and if statements. It prevents actuators from changing to invalid states.

2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

> [!NOTE]
> ***Your Answer***
>
> The context manages the current state, the state interface defines the behavior, and concrete states represent different states. The client requests an action. In our project, ActuatorContext checks whether a state change is allowed. These rules are handled in the domain layer.

3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

> [!NOTE]
> ***Your Answer***
>
> allowed_commands tells the frontend which actions are available for an actuator. This helps the UI show only the correct commands instead of guessing based on the state.

## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

> [!NOTE]
> ***Your Answer***
>
> I implemented five states: off, idle, running, error, and maintenance. An idle actuator can start running, turn off, enter maintenance, or enter error. A running actuator can return to idle or enter error. Error and maintenance states can also move to other allowed states. The system checks these transitions before changing the state.

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

> [!NOTE]
> ***Your Answer***
>
> Actuator states are saved in the actuator_states database table so they are not lost when the backend restarts. After restarting, the system should still show the saved actuator state.

6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

> [!NOTE]
> ***Your Answer***
>
> An illegal transition must not update the database because it could cause incorrect actuator behavior. HTTP 409 Conflict is suitable because the requested change is not allowed in the current state. The rule belongs in the domain so it works independently of the frontend.

7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

> [!NOTE]
> ***Your Answer***
>
> The dashboard uses state to show colored badges for actuators. It uses allowed_commands to show which actions are available. This prepares Phase 10 because the frontend can send commands to the backend, which checks whether they are allowed.

## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

> [!NOTE]
> ***Your Answer***
>
> Both patterns let a context use different behaviors. State changes automatically as an actuator moves through its lifecycle, such as idle to running. Strategy allows choosing different algorithms. In Phase 6, Conservative and Aggressive strategies control greenhouse automation differently.

9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

> [!NOTE]
> ***Your Answer***
>
> Multiple boolean flags can create confusing situations, such as an actuator being running and in maintenance at the same time. Using clear states and transition rules prevents these invalid combinations and makes the system easier to understand.

10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> HTTP status codes belong in the API, and database commits belong in the persistence layer. Putting them inside state classes mixes different responsibilities. Changing a state directly without using transition() also skips validation and may allow an invalid transition. Keeping these parts separate makes the code easier to maintain and test.
