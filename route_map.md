# Promethios API Route Map

**Total Routes:** 33  
**Generated At:** 2025-04-21T09:02:28.676678  
**Version:** 1.0.0  

## Table of Contents

- [Core Routes (5)](#core-routes)
- [Loop Routes (4)](#loop-routes)
- [Agent Routes (10)](#agent-routes)
- [Persona Routes (3)](#persona-routes)
- [Debug Routes (7)](#debug-routes)
- [Other Routes (4)](#other-routes)

## Core Routes

### `GET /health`

Health check endpoint.

**Status Code:** None

**Tags:** core

---

### `GET /system/status`

Get system status including environment and module load state.

**Status Code:** None

**Tags:** core

---

### `POST /memory/read`

Retrieve memory by key.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| key | <class 'str'> | Yes |

**Status Code:** None

**Tags:** core

---

### `POST /memory/write`

Direct memory injection.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** core

---

### `POST /memory/delete`

Clear keys from memory.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, str] | Yes |

**Status Code:** None

**Tags:** core

---

## Loop Routes

### `GET /loop/trace`

Get loop memory trace log.

**Status Code:** None

**Tags:** loop

---

### `POST /loop/trace`

Inject synthetic loop trace.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** loop

---

### `POST /loop/reset`

Memory reset for clean test runs.

**Status Code:** None

**Tags:** loop

---

### `POST /loop/persona-reflect`

Inject mode-aligned reflection trace.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** loop

---

## Agent Routes

### `POST /analyze-prompt`

Thought Partner prompt analysis.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /generate-variants`

Thought Variant Generator.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /plan-and-execute`

HAL, ASH, NOVA execution.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /run-critic`

Loop summary review.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /pessimist-check`

Tone realism scoring.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /ceo-review`

Alignment + Operator satisfaction.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /cto-review`

Trust decay + loop health.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /historian-check`

Forgotten belief analysis.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /drift-summary`

Aggregated loop-level drift.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

### `POST /generate-weekly-drift-report`

Weekly system meta-summary.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** agent

---

## Persona Routes

### `POST /persona/switch`

Change active mode.

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| data | typing.Dict[str, typing.Any] | Yes |

**Status Code:** None

**Tags:** persona

---

### `GET /persona/current`

Return current orchestrator_persona.

**Status Code:** None

**Tags:** persona

---

### `GET /mode/trace`

Trace of persona usage over loops.

**Status Code:** None

**Tags:** persona

---

## Debug Routes

### `GET /api/debug/orchestrator/reflection/{project_id}`

Get the last reflection for a project.

Args:
    project_id: The project identifier
    
Returns:
    The last reflection record
    
Raises:
    HTTPException: If the project doesn't exist or has no reflection

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/orchestrator/reflections/{project_id}`

Get all reflections for a project.

Args:
    project_id: The project identifier
    
Returns:
    Dict containing all reflection records
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/orchestrator/decisions/{project_id}`

Get all orchestrator decisions for a project.

Args:
    project_id: The project identifier
    
Returns:
    Dict containing all decision records
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/orchestrator/execution/{project_id}`

Get all execution log entries for a project.

Args:
    project_id: The project identifier
    
Returns:
    Dict containing all execution log entries
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/orchestrator/deviation/{project_id}`

Check for deviations in the project state that might require intervention.

Args:
    project_id: The project identifier
    
Returns:
    Dict containing identified issues, empty if no issues found
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/orchestrator/reroute/{project_id}`

Get the reroute trace for a project.

Args:
    project_id: The project identifier
    
Returns:
    Dict containing the reroute trace
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

### `GET /api/debug/memory/{project_id}`

Get the entire memory for a project.

Args:
    project_id: The project identifier
    
Returns:
    The project memory
    
Raises:
    HTTPException: If the project doesn't exist

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| project_id | <class 'str'> | Yes |

**Response Model:** Dict

**Status Code:** None

**Tags:** debug

---

## Other Routes

### `HEAD, GET /openapi.json`

No description available

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| req | <class 'starlette.requests.Request'> | Yes |

**Status Code:** 200

---

### `HEAD, GET /redoc`

No description available

**Parameters:**

| Name | Type | Required |
|------|------|----------|
| req | <class 'starlette.requests.Request'> | Yes |

**Status Code:** 200

---

### `GET /docs`

No description available

**Status Code:** None

---

### `GET /`

Root endpoint that returns basic API information.

**Status Code:** None

---

