A. Pattern
State the intent of Factory Method in plain language. What problem appears when callers scatter new / constructors (or a growing if type == ...) across the application?
Note

Factory method keeps object creation in one place. It prevents the application from having many constructors or if/elif statements in different parts of the application. This makes the code easier to change and maintain.

---

Name the main participants of Factory Method (product, concrete product, creator, concrete creator, client). For each, give one sentence: what it is responsible for.
Note

Product: Defines the common types of object.
Concrete Product: It is a specific type of product.
Creator: Defines how the product is created.
Concrete Creator: Creates a specific product.
Client: Uses the creator to get product.

---

How do you add a new product variant when creators are polymorphic (new class + registry entry) versus when creation lives in one shared if/elif function? Why does that difference matter for extension?
Note

with polymorphic creators, we add a new creator class and add it to the registry.

---

B. This phase of the application
In this lab, what is the product and what are the concrete creators? Why must the API handler (or sensor service) go through a creator/registry instead of constructing MoistureSensor / LightSensor itself?
Note

The product is the sensor class. The concrete creators are the MoistureSebsirCreator and LightSensorCreator. The API uses the creator to decide which sensor to create. This keeps the sensors creation out of the API code.

---

POST /api/sensors accepts a short type key such as "moisture" or "light", while the stored/returned field is device_type (for example moisture_sensor). Why are those two fields different? Who decides the stored device_type and default_config?
Note

type is a short key used to choose the creator. devivce_type is the actual type stored in the database. The concrete creator decides the device_type and default_config.

---

Why is there a single devices table with role="sensor" instead of a dedicated sensors table? What later phase does that choice prepare for?
Note

One devices table can store different types of devices. The role="sensor" shows that the device is a sensor. This prepares the project for other devices in

---

What should happen when the client posts an unknown type? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?
Note

The application should reject an unknown type. The registry or service should check the type and return an error. The API should not create a sensor with an invalid type.

---

C. Compare, contrast, and scenarios
Contrast Factory Method with a simple factory (one function full of if type == ...). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?
Note

A simple factory uses one function with if/elif statements. It is good for small applications with only a few types. Factory Method uses separate creator classes. This phase uses Factory Method because it makes adding new sensor types easier.

---

Contrast Factory Method with Abstract Factory (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?
Note

Factory Method decides which single product to create. Abstract Factory creates a group of related products. Factory Method is enough for Phase 2 because we only need to create different types of sensors.

---

A classmate puts SQLAlchemy session commits (or FastAPI request parsing) inside a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?
Note

Putting SQLAlchemy or FastAPI code inside the creator mixes different jobs together. The creator should only create the sensor. HTTP code should stay in the API layer. Database code should stay in the repository or database layer.

---