A. Pattern
In your own words, what is a design pattern? What is it not?
A design pattern is a common way to solve a software design problem. It is not ready made code but is a general idea that we can use when designing our code.

Name the three GoF pattern families. For each family, give one-sentence: what kind of design problem it addresses. Then place Factory Method and Strategy into the correct family.
Creational: It helps with creating objects. Factory Method belongs here.
Structural: It helps with how classes and objects are connected.
Behavioral: It helps with how objects communicate and behave. Strategy belongs here.


A teammate wants to add a pattern “because it is on the course list,” even though the feature is small and unlikely to grow. When should you skip a pattern? What risk do you take if you apply one too early?
We should skip a pattern when the feature is small and simple. If we use a pattern too early, the code can become more complicated than needed. It can also create unnecessary classes and code.


B. This phase of the application
Why does Phase 1 ship a vertical slice that does almost no greenhouse business logic? What does “empty but running” prove that a folder of unimplemented classes would not?
Phase 1 is mainly about building the basic project structure. It checks that the frontend, backend, and database can work together. An empty but running project proves that the system actually works. A folder with empty classes only proves that the files were created.


List the four backend layer packages used in this course (domain, application, infrastructure, interfaces/api). For each, state what belongs there and give one example of something that must not live in domain.
domain: contains the main business concepts and rules.
application: Contains the actions or use cases of the application.
infrastructure: Contains technical things like the database connection.
interfaces/api: Contains API routes such as /health.
FastAPI code should not be inside domain because the domain should not depend on a specific framework.

What does GET /health return, and why does it check the database instead of only reporting that the HTTP process is up? Why is API documentation served at /scalar, and why is /docs disabled?
/health tells us whether the API and databse are working or not.
we use /scalar for API documentation. /docs is disabled because we are not using the default swagger documentation 

Phase 1 requires Alembic (or equivalent) with a baseline migration and no business tables such as devices. Why introduce the migration toolchain before any product schema? What would go wrong if you created tables by hand in Postgres and only added migrations later?
Alembic keeps the track of changes made in database. We use it from the beginning to ensure the same database structure. If we create tables manually first, the database and migration files can become different. This can cause problems when setting up the project on another computer.

C. Compare, contrast, and scenarios
Explain dependency direction in this skeleton: which layers may import which? Why must domain code not import FastAPI, SQLAlchemy, or Pydantic models used as HTTP schemas?
The main idea is that the business logic should stay independent. The domain should not depend on FastAPI, SQLAlchemy, or HTTP schemas. The domain should not care whether we use PostgreSQL or another database. This makes the code easier to change and test later.

The frontend cannot show a healthy badge. A classmate blames “the patterns.” What should you check first (stack, CORS/proxy, health JSON), and why is that a Phase 1 concern rather than a later pattern concern?
If /health works in the browser but the frontend cannot access it, the problem is probably with the frontend connection or CORS.

Course completion is at Phase 12, not Phase 1. What is still missing after a successful skeleton, and how do later phases add behaviour without rewriting the foundations you laid here?
After the phase 1 we only have the basic working structure. The actual greenhouse features are still missing.