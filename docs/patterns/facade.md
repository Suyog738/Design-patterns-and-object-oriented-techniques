## Facade Pattern
---

## Why use facade pattern?
> The Facade Pattern provides one simple entry point to a complex subsystem.  In our Smart Greenhouse project, LocationOverviewFacade gathers the data needed for the dashboard Overview page.It hides the details of retrieving locations, assigned devices, latest sensor readings, and the saved automation strategy. The API handler only needs to call the facade to get the complete overview.

## Last_Recommendation
> The last_recommendation is calculated by calling the existing AutomationService.evaluate() whenever the overview is requested and a strategy is configured. It is computed on each GET request and is not cached in a new database table. If no strategy is configured, strategy_key and last_recommendation are returned as null.

## Querry
> The facade retrieves all assigned devices in one query. It then retrieves the newest reading for each assigned device in one query using a SQL window function. This avoids making a separate latest-reading query for every device.

## Database changes
> This phase does not require a new business table. The existing locations, zones, devices, sensor_readings, and automation_rules tables provide the data needed. The facade combines this existing data into one overview response.