# OpenAPI Documentation for RUL Endpoint

## Remaining Useful Life (RUL) Prediction Endpoint

This document provides OpenAPI 3.0.0 specification for the Remaining Useful Life (RUL) prediction endpoint, which is a critical component of the predictive maintenance platform. This endpoint allows external systems to query the predicted RUL for specific industrial pumps, enabling proactive maintenance scheduling.

### Endpoint: `/rul/{pumpId}`

#### GET /rul/{pumpId}

**Summary:** Retrieve the predicted Remaining Useful Life (RUL) for a specific industrial pump.

**Description:** This endpoint provides the current predicted RUL for a given pump, based on real-time sensor data and historical operational patterns. The RUL is expressed in a quantifiable unit, such as operating hours or days.

**Parameters:**

| Name     | In     | Required | Type   | Description                                |
| :------- | :----- | :------- | :----- | :----------------------------------------- |
| `pumpId` | `path` | `true`   | `string` | Unique identifier of the industrial pump. |

**Responses:**

*   **200 OK**
    *   **Description:** Successfully retrieved the predicted RUL.
    *   **Content:**
        ```json
        {
          "application/json": {
            "schema": {
              "type": "object",
              "properties": {
                "pumpId": {
                  "type": "string",
                  "description": "Unique identifier for the pump."
                },
                "predictedRUL": {
                  "type": "number",
                  "format": "float",
                  "description": "Predicted Remaining Useful Life (e.g., in hours or days)."
                },
                "unit": {
                  "type": "string",
                  "description": "Unit of the predicted RUL (e.g., 'hours', 'days')."
                },
                "timestamp": {
                  "type": "string",
                  "format": "date-time",
                  "description": "Timestamp of the RUL prediction."
                }
              },
              "required": ["pumpId", "predictedRUL", "unit", "timestamp"]
            }
          }
        }
        ```

*   **404 Not Found**
    *   **Description:** The specified `pumpId` was not found, or RUL prediction is not available for this pump.
    *   **Content:**
        ```json
        {
          "application/json": {
            "schema": {
              "type": "object",
              "properties": {
                "message": {
                  "type": "string",
                  "example": "Pump with ID 'pump123' not found or RUL not available."
                }
              }
            }
          }
        }
        ```

*   **500 Internal Server Error**
    *   **Description:** An unexpected error occurred on the server.
    *   **Content:**
        ```json
        {
          "application/json": {
            "schema": {
              "type": "object",
              "properties": {
                "message": {
                  "type": "string",
                  "example": "An internal server error occurred."
                }
              }
            }
          }
        }
        ```

### Example Request:

```http
GET /rul/pump_A101 HTTP/1.1
Host: api.example.com
Accept: application/json
```

### Example Response (200 OK):

```json
{
  "pumpId": "pump_A101",
  "predictedRUL": 1500.5,
  "unit": "hours",
  "timestamp": "2023-10-27T10:30:00Z"
}
```
