\# Employee Management API



A REST API built using Python, Flask, and SQLite to manage employee records.



\## Features



\- Create employees using POST

\- Retrieve employees using GET

\- Update employees using PUT

\- Delete employees using DELETE

\- Input validation and error responses

\- Persistent storage with SQLite



\## Tech Stack



\- Python

\- Flask

\- SQLite

\- REST API

\- HTTP and JSON



\## Setup



```bash

py -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

py app.py

```



\## Endpoints



| Method | Endpoint | Description |

|---|---|---|

| GET | `/` | API health message |

| GET | `/employees` | List all employees |

| POST | `/employees` | Create employee |

| PUT | `/employees/<id>` | Update employee |

| DELETE | `/employees/<id>` | Delete employee |



\## Example POST Request



```json

{

&#x20; "name": "Amit",

&#x20; "role": "Backend Developer"

}

```



The application creates the SQLite database and employee table automatically when it starts.

