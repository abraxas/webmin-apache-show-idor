#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webminh01}"
export PYTHONUNBUFFERED=1
chmod +x poc.py plant.sh

LABEL="WEBMIN-H01-APACHE-SHOW"
WITNESS="WEBMIN-H01-APACHE-IDOR"
IMAGE="webmin-lab:2.670"
LOCK="/tmp/webmin-lab-image.lock"
PIN="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
PIN_TAG="2.670"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
SRC="$(pwd)/src"
DOCKERFILE="$(pwd)/Dockerfile"
BASE="http://127.0.0.1:18490"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  down
  exit 1
}

clone_pin() {
  if [[ -d "${SRC}/.git" ]]; then
    local got
    got="$(git -C "${SRC}" rev-parse HEAD)"
    if [[ "${got}" == "${PIN}" ]]; then
      echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=existing-clone"
      return 0
    fi
    echo "IOC reclone tag=${PIN_TAG} got=${got} expect=${PIN}"
    rm -rf "${SRC}"
  fi
  echo "== git clone ${PIN_TAG} ${PIN} =="
  GIT_TERMINAL_PROMPT=0 git clone --depth 1 --branch "${PIN_TAG}" \
    "${REPO_URL}" "${SRC}" || fail_setup "clone-failed"
  local got
  got="$(git -C "${SRC}" rev-parse HEAD)"
  echo "IOC checkout tag=${PIN_TAG} sha=${got} expect=${PIN}"
  if [[ "${got}" != "${PIN}" ]]; then
    GIT_TERMINAL_PROMPT=0 git -C "${SRC}" fetch --depth 1 origin "${PIN}" \
      || fail_setup "fetch-failed"
    git -C "${SRC}" checkout --detach "${PIN}" || fail_setup "checkout-failed"
    got="$(git -C "${SRC}" rev-parse HEAD)"
    echo "IOC checkout-forced tag=${PIN_TAG} sha=${got}"
  fi
  if [[ "${got}" != "${PIN}" ]]; then
    fail_setup "pin-mismatch"
  fi
  echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=git-clone"
}

ensure_image() {
  python3 - "${LOCK}" "${IMAGE}" "${DOCKERFILE}" "${SRC}" <<'PY'
import fcntl
import os
import subprocess
import sys

lock_path, image, dockerfile, src = sys.argv[1:5]
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o666)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        check=False,
    )
    if inspect.returncode == 0:
        print(f"IOC reuse-image {image}", flush=True)
        raise SystemExit(0)
    print(f"IOC build-image {image}", flush=True)
    raise SystemExit(
        subprocess.call(["docker", "build", "-t", image, "-f", dockerfile, src])
    )
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
PY
}

trap down EXIT

echo "== py_compile =="
python3 -m py_compile poc.py

echo "== pin ${PIN_TAG} ${PIN} =="
clone_pin
if [[ ! -f "${SRC}/setup.sh" ]] || ! grep -qx "${PIN_TAG}" "${SRC}/version"; then
  fail_setup "webmin-src-pin"
fi

echo "== docker compose down (clean) =="
down

echo "== ensure ${IMAGE} =="
ensure_image || fail_setup "image-build-failed"
echo "IOC image=${IMAGE}"

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 8); do
  docker network prune -f >/dev/null 2>&1 || true
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --no-build; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${BASE}/session_login.cgi =="
ready=0
for i in $(seq 1 60); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 \
    "${BASE}/session_login.cgi" || true)"
  if [[ "${code}" == "200" || "${code}" == "401" ]]; then
    ready=1
    echo "IOC webmin-ready attempt=${i} http=${code}"
    break
  fi
  echo "IOC webmin-wait attempt=${i} http=${code}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  fail_setup "webmin-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py
rc=$?
set -e

if [[ "${rc}" -ne 0 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
fi

if [[ ! -f poc-last-run.txt ]] || ! tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit-${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"
