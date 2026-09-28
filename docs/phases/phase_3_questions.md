# Phase 3 — Abstract Factory questions

**Pattern / focus:** Abstract Factory.

**Read first:** [Guide 03](../../materials/guides/03-abstract-factory.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

> [!NOTE]
> ***Your Answer***
>
> Abstract Factory creates related products as one family. It prevents incompatible products from being mixed. Separate if statements can accidentally choose products from different families.

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

> [!NOTE]
> ***Your Answer***
>
> The abstract factory defines the factory. The concrete factory creates a specific family. Abstract products define common products. Concrete products are the actual products. The client uses the factory. Choosing a factory means using that factory's family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

> [!NOTE]
> ***Your Answer***
>
> We should use Abstract Factory when several related products must work togetherand skip it when only one product is needed or when mixing products is allowed.

## B. This phase of the application
The abstract factory defines the factory. The concrete factory creates a specific family. Abstract products define common products. Concrete products are the actual products. The client uses the factory. Choosing a factory means using that factory's family.
4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

> [!NOTE]
> ***Your Answer***
>
> A device family is a group of related devices. In this application, the families are simulation and edge. create_device_set() returns two sensors and two actuators. They should not mix because they use different configurations and protocols.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

> [!NOTE]
> ***Your Answer***
>
> Abstract Factory uses the Phase 2 sensor creators to create sensors. It does not replace them. Deleting them would cause duplicated construction code and make the code harder to maintain.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

> [!NOTE]
> ***Your Answer***
>
> device_family identifies which family each device belongs to. Using one table keeps the database simple. Old Phase 2 rows need a default value. Without it, they may fail because the new column is required.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

> [!NOTE]
> ***Your Answer***
>
> The UI needs family filtering to show the correct devices. It prevents simulation and edge devices from being mixed. The old /api/sensors routes must still work because Phase 3 should not break Phase 2.

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

> [!NOTE]
> ***Your Answer***
>
> Factory Method focuses on which one product to create. Abstract Factory focuses on which product line to create. Abstract Factory can use Factory Method-style methods inside it.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

> [!NOTE]
> ***Your Answer***
>
> It can create devices with the wrong family or protocol. This can make the device set inconsistent. The HTTP handler should call the service, and the service should use the family factory.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

> [!NOTE]
> ***Your Answer***
>
> A god factory has too many responsibilities. Locations, readings, and devices are not one product family. Separate factories keep the code simple and easier to maintain.
