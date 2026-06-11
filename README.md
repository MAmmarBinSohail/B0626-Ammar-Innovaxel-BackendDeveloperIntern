# Event Registration System API

* **Full Event & Registration Management**: Supports creating unique events with future dates, registering users with real-time timestamps, and managing cancellations cleanly.
* **Real-Time Seat Tracking**: Dynamically calculates available seats and total registrations per event, ensuring cancelled seats instantly become available again.
* **Advanced Query Filters**: Includes built-in parameters to seamlessly filter only upcoming events and sort the entire list by date.
* **Race Condition Protection**: Uses database-level row locking to completely prevent overbooking when multiple users register at the exact same millisecond.
* **Strict Validation & Edge-Case Handling**: Blocks duplicate event names, double-registrations by the same user, and invalid dates, returning explicit HTTP error codes for all failures.
* **Interactive API Documentation**: Automatically generates full testing suites accessible directly via FastAPI's built-in Swagger UI (/docs) endpoint.
