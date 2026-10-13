# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

**Read first:** [Guide 06](../../materials/guides/06-strategy.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example shipping quotes) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to irrigation (or lighting) policies, location context, and the automation API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?

> [!NOTE]
> ***Your Answer***
>
> Strategy allows us to choose between different algorithms without changing the context. The context uses a selected strategy to run the algorithm. Choosing and running the algorithm should be separate to keep the code flexible and easy to maintain.

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?

> [!NOTE]
> ***Your Answer***
>
> The participants are Strategy, Concrete Strategies, Context, and Client. If all policies are inside if/elif statements, the code becomes harder to maintain and extend. HTTP routers should handle requests, not contain business logic.

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy)?

> [!NOTE]
> ***Your Answer***
>
> Use Strategy when there are multiple algorithms that can be switched and skip it when there is only one algorithm or when the change represents a lifecycle state rather than a policy.

## B. This phase of the application

4. In this lab, what does a strategy’s `decide(context)` return (action + reason)? Give a concrete difference you implemented (or were required to implement) between **conservative** and **aggressive** on the **same** moisture reading and zone thresholds.

> [!NOTE]
> ***Your Answer***
>
> The decide(context) method returns an action and a reason. Conservative waits when moisture is still within the safe range, while Aggressive may recommend irrigation sooner using the same moisture reading and zone thresholds.

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?

> [!NOTE]
> ***Your Answer***
>
> The context gets moisture readings from sensor_readings and thresholds from the zone configuration. This phase uses existing data, so it does not need a new scheduler or MQTT broker. A plain context object keeps strategies independent of database and HTTP frameworks. Thresholds come from zones so each zone can have its own settings.

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

> [!NOTE]
> ***Your Answer***
>
> The evaluation endpoint must use the saved strategy key so the selected policy stays consistent between requests. When the operator changes the saved strategy, the next evaluation uses the new strategy, even if the moisture reading stays the same.

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?

> [!NOTE]
> ***Your Answer***
>
> The strategy only recommends whether to irrigate or wait. Keeping decisions separate from execution prevents the strategy from directly controlling hardware. The Command pattern can later be used to carry out the action.

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

> [!NOTE]
> ***Your Answer***
>
> In Strategy, the client or configuration selects the active algorithm. In State, the object's lifecycle usually determines when the active state changes. Strategy changes a policy, while State represents a lifecycle condition.

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

> [!NOTE]
> ***Your Answer***
>
> Adapter: Translates an external API into the interface our application expects.
> Builder: Assembles a valid object or aggregate step by step.
> Strategy: Allows different algorithms to be selected and used.

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> A mega-strategy with if/elif statements still combines all policies in one class, so it loses the main benefit of Strategy. A strategy that calls the actuator directly mixes decision-making with execution, making the code harder to test and maintain.
