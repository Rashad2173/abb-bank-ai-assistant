from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from service_common import DependencyUnavailable, create_app, dependency, request_id


def make_app(checks):
    app = create_app("demo", "1.0", ready_checks=lambda app: checks)

    class Body(BaseModel):
        n: int

    @app.post("/echo")
    async def echo(body: Body):
        return {"n": body.n, "request_id": request_id()}

    @app.get("/missing")
    async def missing():
        raise HTTPException(404, "no such thing")

    @app.get("/down")
    async def down():
        with dependency("Milvus"):
            raise ConnectionError("refused")

    @app.get("/boom")
    async def boom():
        raise ValueError("bug")

    return app


async def ok() -> str:
    return "fine"


async def failing() -> str:
    raise ConnectionError("refused")


def test_health_does_not_check_dependencies():
    client = TestClient(make_app({"db": failing}))
    assert client.get("/health").json() == {"status": "ok", "service": "demo", "version": "1.0"}


def test_ready_reports_every_check_and_fails_with_503():
    assert TestClient(make_app({"db": ok})).get("/ready").json()["status"] == "ready"

    response = TestClient(make_app({"db": ok, "milvus": failing})).get("/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["db"]["ok"] and not body["checks"]["milvus"]["ok"]
    assert "ConnectionError" in body["checks"]["milvus"]["detail"]


def test_request_id_is_taken_from_the_caller_and_returned():
    response = TestClient(make_app({})).post("/echo", json={"n": 1}, headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"
    assert response.json()["request_id"] == "abc123"


def test_errors_are_json_with_a_code_and_the_request_id():
    client = TestClient(make_app({}), raise_server_exceptions=False)

    invalid = client.post("/echo", json={"n": "x"}, headers={"X-Request-ID": "r1"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_request" and invalid.json()["request_id"] == "r1"

    assert client.get("/missing").json()["error"] == {"code": "not_found", "message": "no such thing"}

    down = client.get("/down")
    assert down.status_code == 503 and down.json()["error"]["code"] == "dependency_unavailable"
    assert "Milvus is unavailable" in down.json()["error"]["message"]

    boom = client.get("/boom", headers={"X-Request-ID": "r2"})
    assert boom.status_code == 500
    assert boom.json() == {
        "error": {"code": "internal_error", "message": "Internal error - see the service log for this request id."},
        "request_id": "r2",
    }


def test_dependency_only_wraps_the_given_errors():
    try:
        with dependency("OpenAI", TimeoutError):
            raise TimeoutError
    except DependencyUnavailable as exc:
        assert exc.dependency == "OpenAI"
    try:
        with dependency("OpenAI", TimeoutError):
            raise KeyError("bug")
    except KeyError:
        pass
