# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

> [!NOTE]
> ***Your Answer***
>
> A decorator wraps an object and adds extra behaviour without changing the object itself. With subclasses, we would need a new class for every combination of features, for example logging only, max run time only, or both. With decorators, each feature is one small class, and we combine them by wrapping one inside another.


2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

> [!NOTE]
> ***Your Answer***
>
> _The component is `ActuatorPort`. The concrete component is `SimulationActuatorAdapter`. The decorators are classes that implement `ActuatorPort` and hold another `ActuatorPort` inside. The concrete decorators are `LoggingActuatorDecorator` and `MaxRunTimeActuatorDecorator`. Every decorator has the same `apply(device_id, command, payload)` method. It must match so the caller can use a wrapped port exactly like the real adapter, and so decorators can be stacked on each other.

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

> [!NOTE]
> ***Your Answer***
>
> In our project, logging wraps max run time. When max run time blocks a command, logging still sees the error and saves a failed row. If we reversed the order, max run time would block the command before it reached logging, so the blocked attempt would not be saved at all.


## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

> [!NOTE]
> ***Your Answer***
>
> `ActuatorPort` is the interface for sending a command to an actuator, with one method `apply()`. We stacked `LoggingActuatorDecorator` and `MaxRunTimeActuatorDecorator` around `SimulationActuatorAdapter`. The chain is built in `build_actuator_port()` in the application service. It is not in the router because the router should only handle HTTP requests and responses. Keeping the chain in one place makes it easy to change and test.


5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

> [!NOTE]
> ***Your Answer***
>
> A blocked attempt is still an important event. Saving it shows that someone tried to send a command and that the safety rule stopped it. The policy name in `policy_applied` shows which rule blocked it, so the user does not have to guess why the command failed.


6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

> [!NOTE]
> ***Your Answer***
>
> The decorator reads the actuator's state and `updated_at` from the `actuator_states` table. If the state is `running` and `updated_at` is at least 30 minutes old, it blocks the command. This data comes from the State pattern because State already manages the actuator lifecycle. If the decorator kept its own timer or state, the two could disagree.


7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

> [!NOTE]
> ***Your Answer***
>
> Printed logs are hard to find and are lost when the server restarts. Saving attempts in the database keeps a history that the API and the dashboard can show. After a blocked attempt and a refresh, the UI should show a new row with a red failed badge, the policies `maxRunTime` and `logging`, and the message "Max run time exceeded".


## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

> [!NOTE]
> ***Your Answer***
>
> The decorator keeps the same interface and adds behaviour. In Phase 9, the logging and max run time decorators keep `ActuatorPort.apply()` and add checks. The adapter changes the interface and translates data. In Phase 5, sensor adapters like `VendorStubSensorAdapter` convert raw vendor data into our own sensor reading format.


9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

> [!NOTE]
> ***Your Answer***
>
> With inheritance, every combination of policies needs its own subclass, and the number of classes grows quickly. With composition, each policy is a separate decorator. To add or remove a policy, we only change how the chain is built in `build_actuator_port()`. No new class is needed for each combination.


10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> If a decorator changes the method signature, it no longer matches `ActuatorPort`. The caller cannot use it like the real adapter, and it cannot be stacked with other decorators. Ignoring wrap order is also a trap because the order changes the result. For example, if logging is outside a retry decorator, it logs once per call. If it is inside, it logs every retry attempt, and blocked attempts might not be logged at all.
