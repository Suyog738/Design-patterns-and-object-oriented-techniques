# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
> ***Your Answer***
>
> Adapter helps two different interfaces work together. It changes data from an external system into the format our application understands. Without an adapter, the application would need to understand vendor-specific names, units, and formats.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
> ***Your Answer***
>
> The target/port is SensorPort. The adaptee is the external sensor or data format. The adapter changes the external data into our format. The client is the application service. The adapter should only translate data and should not make business decisions.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
> ***Your Answer***
>
> Modern code usually uses an object adapter with composition. It is more flexible and avoids strong connections between classes through inheritance.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
> ***Your Answer***
>
> SensorPort is the common interface for our sensors. Adapters return a common Reading object with the value, unit, source, device ID, and time. The application uses SensorPort so it does not need to know if the data comes from simulation, a vendor, or MQTT.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
> ***Your Answer***
>
> Different sensors can send data in different formats. Adapters change them into the same Reading format. The source shows where the reading came from. MQTT only translates data in this phase and does not connect to a broker or HTTP.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
> ***Your Answer***
>
> We save all readings to keep sensor history for later phases. All readings use the same writer so they are saved consistently. The sampler skips tracking-off and MQTT devices. The sensor cards poll the latest reading until Phase 12 uses WebSocket.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
> ***Your Answer***
>
> If the device does not exist, the API should return 404 Not Found. If the adapter receives invalid data, it should return 400 Bad Request. The router should only work with our normal Reading and DTO types, not vendor-specific data.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
> ***Your Answer***
>
> An Adapter changes the format of something so the application can use it. For example, a vendor sensor value is changed into a Reading.
> A Facade makes things easier to use. For example, a Phase 7 facade could give one simple way to get greenhouse information instead of calling several services separately.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
> ***Your Answer***
>
> An Adapter changes the interface so two different systems can work together. A Decorator keeps the same interface but adds extra behavior, such as logging or caching.

10. A classmate puts irrigation policy (“if moisture &lt; 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
> ***Your Answer***
>
> The adapter should not decide when to water the plants. Its job is only to convert the sensor data into a Reading. The irrigation decision should be handled later by a Strategy, where the business rules belong.
