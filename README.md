![Project Logo](doc/main.PNG)

# Project Overview

This project is a web application built using FastAPI. It provides a user interface for managing items, includes authentication, and supports real-time communication through WebSocket. The application uses SQLite as the database and is served by `uvicorn`. Nginx is used as a reverse proxy and to serve static files.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Routes](#routes)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- User authentication and registration
- Item management (add, update, list)
- Admin dashboard for user management
- Real-time notifications using WebSocket
- Download data as CSV
- Responsive HTML templates

## Architecture

The architecture of this project includes the following components:

1. **Client (Browser)**: The client sends HTTP requests and receives responses.
2. **Nginx**: Acts as a reverse proxy to forward requests to the FastAPI application and serves static files.
3. **FastAPI Application**: Handles the core logic of the application, including routing, database operations, and real-time communication.
4. **Uvicorn**: An ASGI server used to run the FastAPI application.
5. **SQLite**: The database used to store application data.
6. **WebSocket**: Provides real-time communication capabilities.

### Workflow Diagram

```plaintext
+-------------------+      +-------+       +----------------+      +--------+      +-----------+
|                   |      |       |       |                |      |        |      |           |
|   Client Browser  +------> Nginx +-------> FastAPI (app)  +------> Uvicorn +------> SQLite DB |
|                   |      |       |       |                |      |        |      |           |
|  (HTTP Requests)  |      |       |       |    (ASGI App)  |      |        |      |           |
+-------------------+      +-------+       +----------------+      +--------+      +-----------+
             ^                    |                    ^                   |               ^
             |                    |                    |                   |               |
             |                    |                    |                   |               |
             |                    |                    |                   |               |
             |                    |                    |                   |               |
             |                    v                    |                   v               |
             |          +------------------+           |           +----------------+      |
             |          |  Static Files    |           |           |                |      |
             |          |  (CSS, JS, etc.) |           |           |   WebSocket    |      |
             |          +------------------+           |           |                |      |
             |                                         |           +----------------+      |
             |                                         |                                    |
             v                                         v                                    v
    +------------------+                  +-------------------+                 +----------------+
    |  HTML Templates  |                  |     API Routes    |                 |   DB Queries   |
    |  (Jinja2)        |                  |  (user, item, admin)|                 |   (SQLAlchemy) |
    +------------------+                  +-------------------+                 +----------------+
