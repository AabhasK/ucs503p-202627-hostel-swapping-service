# API Reference

Generated from the app's OpenAPI schema. Interactive docs, always in
step with the code, are served by every running server at `/docs`, for
example <https://hostelswap.aakashchawla.space/docs>. Requests and responses are JSON. The session is an httpOnly
cookie set by `POST /api/auth/login`. Errors: `401` not signed in,
`403` wrong role, `404` no such item, `409` not allowed in the current
state, `503` no database configured.

## Pages

| Method | Path | Purpose | Body / query |
|---|---|---|---|
| `GET` | `/` | Redirects to `/login`. |  |
| `GET` | `/login` | Sign-in page. |  |
| `GET` | `/student` | Student page (React app). |  |
| `GET` | `/admin` | Warden page (React app). |  |

## Diagnostics

Requires: None.

| Method | Path | Purpose | Body / query |
|---|---|---|---|
| `GET` | `/api/schema` | Live database tables and columns, to check the database is reachable and migrated. |  |
| `GET` | `/api/demo` | Run the engine on the cohort (the database's, or the built-in 30 students without one), Murty budget `k`. | `k`? |

## Authentication

Requires: None for login; a session for the rest.

| Method | Path | Purpose | Body / query |
|---|---|---|---|
| `POST` | `/api/auth/login` | Sign in with a roll number or email; sets the session cookie. | `identifier`: string, `password`: string |
| `POST` | `/api/auth/logout` | Sign out; deletes the session. |  |
| `GET` | `/api/auth/me` | The signed-in user and their role. |  |

## Student

Requires: A student session.

| Method | Path | Purpose | Body / query |
|---|---|---|---|
| `GET` | `/api/student/room` | The student's current room and bed. |  |
| `GET` | `/api/student/round` | The current round for the student's hostel and whether they are enrolled. |  |
| `POST` | `/api/student/round/{round_id}/enroll` | Join or leave an open round. | `enrolled`: boolean |
| `GET` | `/api/student/round/{round_id}/room-types` | Room types the student may ask for in this round. |  |
| `GET` | `/api/student/round/{round_id}/priorities` | The student's saved priorities. |  |
| `PUT` | `/api/student/round/{round_id}/priorities` | Replace the student's priorities (open rounds only). | `priorities`: list of PriorityItem |
| `GET` | `/api/student/round/{round_id}/roommate` | Roommate request sent, and requests received. |  |
| `POST` | `/api/student/round/{round_id}/roommate` | Ask another student to be a roommate. | `rollNo`: string |
| `DELETE` | `/api/student/round/{round_id}/roommate` | Withdraw the roommate request. |  |
| `POST` | `/api/student/roommate-requests/{request_id}/respond` | Accept or refuse a roommate request. | `accept`: boolean |
| `GET` | `/api/student/round/{round_id}/results` | Up to three chains for this student, best first. |  |
| `POST` | `/api/student/round/{round_id}/chains/offer` | Offer a chain; it becomes a proposal with a three-day deadline. | `optionKind`: string, `chainNo`: integer |
| `GET` | `/api/student/proposals` | Proposals that include the student. |  |
| `POST` | `/api/student/proposals/{proposal_id}/respond` | Accept or reject a proposal; one rejection ends it. | `accept`: boolean |

## Warden

Requires: A warden (admin) session.

| Method | Path | Purpose | Body / query |
|---|---|---|---|
| `GET` | `/api/admin/hostels` | All hostels. |  |
| `GET` | `/api/admin/hostels/{hostel_id}/round` | The hostel's latest round that is not cancelled. |  |
| `PUT` | `/api/admin/hostels/{hostel_id}/room-types` | Declare how many rooms of a type the hostel has. | `roomType`: string, `quantity`: integer |
| `GET` | `/api/admin/hostels/{hostel_id}/room-types` | The hostel's declared room types. |  |
| `POST` | `/api/admin/rounds` | Create a draft round for a hostel. | `hostelId`: string |
| `POST` | `/api/admin/rounds/{round_id}/open` | Open a draft round for registration. |  |
| `POST` | `/api/admin/rounds/{round_id}/cancel` | Cancel a round; its open proposals are withdrawn. |  |
| `POST` | `/api/admin/proposals/{proposal_id}/cancel` | Withdraw one proposal still collecting replies. |  |
| `POST` | `/api/admin/rounds/{round_id}/lock-and-run` | Close registration and run the engine (`k`: Murty budget, `max_chain`: chain cap). | `k`?, `max_chain`? |
| `GET` | `/api/admin/rounds/{round_id}/summary` | Counts for the round: enrolled, chains, offers, executed. |  |
| `GET` | `/api/admin/rounds/{round_id}/proposals` | Every proposal in the round with each member's reply. |  |

## Nested types

- `PriorityItem`: `criterion`: string, `value`: string, `weight`?: number
