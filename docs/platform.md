# Backing Platform — Twenty CRM

`twenty-mcp` is a **client** of a Twenty CRM instance. This page provides a Docker
recipe for deploying one locally to serve as the target of `TWENTY_URL`. For
production topologies, follow the upstream
[Twenty self-hosting documentation](https://twenty.com/developers/section/self-hosting).

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack that mirrors [`services/`](https://github.com/Knuckles-Team).
    Systems offered only as a managed service have no local recipe.

## Single-node deployment (Compose)

Twenty publishes the `twentycrm/twenty` image. The following stack runs the server on
`:3000` with its required PostgreSQL and Redis backing services:

```yaml
# docker/twenty-platform.compose.yml
services:
  twenty:
    image: twentycrm/twenty:latest
    container_name: twenty
    hostname: twenty
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - SERVER_URL=http://localhost:3000
      - FRONTEND_URL=http://localhost:3000
      - PG_DATABASE_URL=postgresql://twenty:twenty@twenty-db:5432/twenty
      - REDIS_URL=redis://twenty-redis:6379
      - STORAGE_TYPE=local
      - ACCESS_TOKEN_SECRET=change_me_access_secret
      - REFRESH_TOKEN_SECRET=change_me_refresh_secret
      - ENCRYPTION_KEY=change_me_encryption_key
    depends_on:
      - twenty-db
      - twenty-redis

  twenty-db:
    image: postgres:16-alpine
    container_name: twenty-db
    environment:
      - POSTGRES_DB=twenty
      - POSTGRES_USER=twenty
      - POSTGRES_PASSWORD=twenty
    volumes:
      - twenty_db:/var/lib/postgresql/data

  twenty-redis:
    image: redis:7-alpine
    container_name: twenty-redis

volumes:
  twenty_db:
```

```bash
docker compose -f docker/twenty-platform.compose.yml up -d

# Wait for the server to answer
curl -s http://localhost:3000/healthz
```

Open `http://localhost:3000`, complete the first-run sign-up, then create a developer
**API key** from **Settings → APIs & Webhooks** to use as `TWENTY_TOKEN`.

## Connect twenty-mcp

```bash
export TWENTY_URL=http://localhost:3000
export TWENTY_TOKEN=your_developer_access_token
export TWENTY_MCP_SSL_VERIFY=True

twenty-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Combined deployment

A combined stack places Twenty and the MCP server on one Docker network, so the
server reaches the CRM by container name:

```yaml
# docker/stack.compose.yml
services:
  twenty:
    image: twentycrm/twenty:latest
    hostname: twenty
    ports: ["3000:3000"]
    environment:
      - PORT=3000
      - SERVER_URL=http://twenty:3000
      - PG_DATABASE_URL=postgresql://twenty:twenty@twenty-db:5432/twenty
      - REDIS_URL=redis://twenty-redis:6379
      - STORAGE_TYPE=local
      - ACCESS_TOKEN_SECRET=change_me_access_secret
      - REFRESH_TOKEN_SECRET=change_me_refresh_secret
      - ENCRYPTION_KEY=change_me_encryption_key
    depends_on: [twenty-db, twenty-redis]

  twenty-db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=twenty
      - POSTGRES_USER=twenty
      - POSTGRES_PASSWORD=twenty
    volumes: ["twenty_db:/var/lib/postgresql/data"]

  twenty-redis:
    image: redis:7-alpine

  twenty-mcp:
    image: knucklessg1/twenty-mcp:latest
    depends_on: [twenty]
    environment:
      - TWENTY_URL=http://twenty:3000
      - TWENTY_TOKEN=your_developer_access_token
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]

volumes:
  twenty_db:
```

```bash
docker compose -f docker/stack.compose.yml up -d
```
