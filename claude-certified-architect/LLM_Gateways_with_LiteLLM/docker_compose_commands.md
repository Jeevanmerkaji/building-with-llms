# Docker Compose - Full Command Flow

One continuous run: check Compose is ready, build both services, run
them together, run them individually, push to Docker Hub, then clean
up completely. Every command has a comment explaining what it does and
why, in simple words.

This project's buildable services (app, eval) live in
docker-compose_new.yaml, not the default docker-compose.yml (that one's
the LiteLLM proxy + Postgres stack) - every command below explicitly
passes -f docker-compose_new.yaml for that reason.

```bash
# ============================================================
# STEP 1 - Is Docker Compose here, and ready?
# ============================================================
docker --version
docker compose version
docker ps
# if this errors with "cannot connect to the Docker daemon", start
# Docker Desktop first.


# ============================================================
# STEP 2 - What's already here?
# ============================================================
docker compose -f docker-compose_new.yaml ps -a
docker images


# ============================================================
# STEP 3 - Same env-file fix as the docker branch
# Compose's env_file: is actually more lenient than plain `docker run
# --env-file` (it handles our .env's spaces/quotes fine, verified via
# `docker compose config`) - so this step is here for completeness /
# in case you also run things with plain `docker run` elsewhere, not
# because Compose itself needs it.
#
# For this project, docker-compose_new.yaml already overrides PROXY_URL
# to http://host.docker.internal:4000 for both services, so you don't
# need to hand-edit .env.docker just to run these Compose commands.
# ============================================================
sed -E 's/^([A-Z_]+)\s*=\s*"?([^"]*)"?\s*$/\1=\2/' .env > .env.docker


# ============================================================
# STEP 4 - Build both services' images
# One Dockerfile, two images: "app" and "eval" - same dependencies,
# different command (see docker-compose_new.yaml).
# ============================================================
docker compose -f docker-compose_new.yaml build

docker images | grep -i llm_gateways_with_litellm


# ============================================================
# STEP 5 - Run BOTH services together
# --profile tools includes "eval" too (normally hidden - see Step 6).
# Watch what happens: "app" stays running (it's a service), "eval"
# runs evaluate.py once and then EXITS on its own (it's a job, not a
# service) - that's expected, not a crash.
#
# Also - "eval" needs your actual LiteLLM proxy stack (docker-compose.yml)
# already running and reachable, since it calls it over the network.
# Start that first if it isn't up: docker compose -f docker-compose.yml up -d
# ============================================================
docker compose -f docker-compose_new.yaml --profile tools up -d

docker compose -f docker-compose_new.yaml ps -a
# ^ you should see "app" as Up, and "eval" as Exited (0) - that's correct


# ============================================================
# STEP 6 - Tear that down, then run just ONE service at a time
# ============================================================
docker compose -f docker-compose_new.yaml down

# just the app (this is the normal way to start it - eval's profile
# keeps it out automatically, no flag needed)
docker compose -f docker-compose_new.yaml up -d app
docker compose -f docker-compose_new.yaml ps
# check http://localhost:8501 - the app, running

# just the eval job, on demand, whenever you actually want to spend
# the API budget it costs to run a real evaluation
docker compose -f docker-compose_new.yaml run --rm eval


# ============================================================
# STEP 7 - Push the app image to Docker Hub
# Compose names images "<project>-<service>" by default - ours are
# "llm_gateways_with_litellm-app" and "llm_gateways_with_litellm-eval".
# Since both come from the exact same Dockerfile, in real projects
# you'd usually only push the one you actually deploy (app) - shown
# here pushing both for completeness.
# ============================================================
docker login

docker tag llm_gateways_with_litellm-app jeevan535510/litellm-gateway-app:latest
docker tag llm_gateways_with_litellm-eval jeevan535510/litellm-gateway-eval:latest

docker push jeevan535510/litellm-gateway-app:latest
docker push jeevan535510/litellm-gateway-eval:latest


# ============================================================
# STEP 8 - Delete locally, then pull back down to prove it's real
# ============================================================
docker rmi jeevan535510/litellm-gateway-app:latest jeevan535510/litellm-gateway-eval:latest

docker pull jeevan535510/litellm-gateway-app:latest
docker images | grep -i litellm-gateway


# ============================================================
# STEP 9 - Terminate everything
# Stop the app, remove all containers/network Compose created, delete
# every image (local build names + Docker Hub tags), log out.
# ============================================================
docker compose -f docker-compose_new.yaml down

docker rmi llm_gateways_with_litellm-app llm_gateways_with_litellm-eval jeevan535510/litellm-gateway-app:latest jeevan535510/litellm-gateway-eval:latest

docker logout

# confirm everything is really gone
docker compose ps -a
docker images

# ============================================================
# DONE - docker-compose branch flow complete.
# ============================================================
```
