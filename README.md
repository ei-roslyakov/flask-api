![example workflow](https://github.com/ei-roslyakov/flask-api/actions/workflows/tests.yml/badge.svg)

# How to run API

## Option 1: Run locally

### You have to install all libraries using command (in app folder)

```sh
pip3 install -r requirements-dev.txt
```

### Run api via command (in app folder)

```sh
python3 -m app.app
```

## Option 2: Run with Docker

### Build Docker image

```sh
docker build -t flask-api .
```

### Run Docker container

```sh
docker run -p 5000:5000 flask-api
```

### Run Docker container with environment variables (if needed)

```sh
docker run -p 5000:5000 \
  -e DB_NAME=api \
  -e DB_HOST=localhost \
  -e DB_USER=api \
  -e DB_PASS=1234qwe \
  flask-api
```

## Option 3: Run with Docker Compose (Recommended)

This option sets up both the Flask API and PostgreSQL database automatically.

### Start all services

```sh
docker-compose up -d
```

### View logs

```sh
docker-compose logs -f
```

### Stop all services

```sh
docker-compose down
```

### Stop and remove volumes (data will be lost)

```sh
docker-compose down -v
```

The application will be available at `http://localhost:5000` and the PostgreSQL database at `localhost:5432`.

## Environment variables

| Env                 | Description                                | Default                                                            |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| `DB_NAME`           | DB_NAME                          | `api`                                                                 |
| `DB_HOST`         | DB_HOST                                 | `localhost`                                                                   |
| `DB_USER`         | DB_USER                                 | `api`                                                                   |
| `DB_PASS`         | DB_PASS                                 | `1234qwe`                                                                   |



## How to view data in API

You need to init data in DB, for this you need to run next command.

**For local development (port 5000):**

```sh
curl -X POST http://localhost:5000/api/v1/init_data
```

**For Docker Compose (port 5000):**

```sh
curl -X POST http://localhost:5000/api/v1/init_data
```

## How to view information for all users

**For local development:**

```sh
curl http://localhost:5000/api/v1/users
```

**For Docker Compose:**

```sh
curl http://localhost:5000/api/v1/users
```

## How to view information about specific user

**For local development:**

```sh
curl -i http://localhost:5000/api/v1/users/USER_ID
```

**For Docker Compose:**

```sh
curl -i http://localhost:5000/api/v1/users/USER_ID
```

## How to add user to db

**For local development:**

```sh
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"USER_NAME", "last_name":"LAST_NAME", "description":"POSITION"}' http://localhost:5000/api/v1/users
```

**For Docker Compose:**

```sh
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"USER_NAME", "last_name":"LAST_NAME", "description":"POSITION"}' http://localhost:5000/api/v1/users
```

## How to delete user from db

**For local development:**

```sh
curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1/users/USER_ID
```

**For Docker Compose:**

```sh
curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1/users/USER_ID
```

## How to change information about specific user

**For local development:**

```sh
curl -i -H "Content-Type: application/json" -X PUT -d '{"description":"new_position", "employee": true or false}' http://localhost:5000/api/v1/users/USER_ID
```

**For Docker Compose:**

```sh
curl -i -H "Content-Type: application/json" -X PUT -d '{"description":"new_position", "employee": true or false}' http://localhost:5000/api/v1/users/USER_ID
```
