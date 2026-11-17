# Phase 10 — Command questions

**Pattern / focus:** Command.

**Read first:** [Guide 10](../../materials/guides/10-command.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example editor undo commands) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to command objects, the invoker, `command_log`, and the controls UI from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

> [!NOTE]
> **_Your Answer_**
>
> Command wraps a request like "start pump" in an object. Because it's an object, we can check it, save it to command_log, show it as history, queue it or undo it. A plain actuator.start() just runs and leaves no trace.

2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

> [!NOTE]
> **_Your Answer_**
>
> - Command: StartPumpCommand, StopPumpCommand, SetLightLevelCommand.
> - Client: CommandService creates the command.
> - Invoker: CommandInvoker.run() calls execute().
> - Receiver: the ActuatorPort, which actually moves the hardware.

3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

> [!NOTE]
> **_Your Answer_**
>
> Before the change. Once the change happens, the old value (such as the previous light level) is lost, so undo would have nothing to restore.

## B. This phase of the application

4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

> [!NOTE]
> **_Your Answer_**
>
> start_pump, stop_pump and set_light_level. The router only handles HTTP. The service does the state check, decorators and logging in one place. Calling the adapter from the router would skip all three.

5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

> [!NOTE]
> **_Your Answer_**
>
> Check allowed_commands. If the command isn't allowed, save rejected and stop. If it is, run it through the decorators, update the state and save success or failed. A rejected command must not run, otherwise something illegal happens (like starting a running pump again) and the stored state becomes wrong.

6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

> [!NOTE]
> **_Your Answer_**
>
> - success: it ran. start_pump on an idle pump.
> - rejected: not allowed right now. start_pump on a running pump.
> - failed: allowed, but blocked while running. stop_pump hits "Max run time exceeded".

7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

> [!NOTE]
> **_Your Answer_**
>
> command_log records what the user asked for. actuator_execution_log records what actually reached the actuator. A rejected command only appears in command_log.

## C. Compare, contrast, and scenarios

8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

> [!NOTE]
> **_Your Answer_**
>
> Strategy decides what should happen. The Phase 6 conservative and aggressive strategies return a recommendation and change nothing. Command does something: it changes the actuator and leaves a history. They work together like this: Strategy suggests an action such as "irrigate", and a Command such as start_pump carries it out and logs it.

9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?

> [!NOTE]
> **_Your Answer_**
>
> The user triggers the command. State decides whether it's allowed. If commands skip State, illegal actions run and the saved state becomes wrong.



10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

> [!NOTE]
> **_Your Answer_**
>
> Anyone can call the API without the UI, for example from Scalar or curl, so the backend must check too. If a command calls the raw adapter, illegal actions run, there's no max-run-time limit and nothing gets logged.
