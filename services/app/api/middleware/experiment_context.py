from contextvars import ContextVar
from starlette.types import ASGIApp, Receive, Scope, Send

from app.db.session import SessionLocal
from app.analytics.experiment_service import ExperimentService

# Context variable to store experiment assignments
_experiment_context: ContextVar[dict[str, str]] = ContextVar("experiments", default={})


def get_experiment_context() -> dict[str, str]:
    """Get the current experiment context (assignments for this request)."""
    return _experiment_context.get()


def get_variant_for_experiment(experiment_name: str) -> str | None:
    """Get the variant assigned to the user for a specific experiment."""
    return get_experiment_context().get(experiment_name)


class ExperimentContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Build a fake Request just to access .state
        from starlette.requests import Request
        request = Request(scope, receive)

        experiment_assignments = {}
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id

        if user_id:
            db = SessionLocal()
            try:
                service = ExperimentService(db)
                for experiment_name in service.get_all_active_experiments():
                    try:
                        variant = service.assign_user_to_variant(user_id, experiment_name)
                        experiment_assignments[experiment_name] = variant
                    except Exception:
                        pass
            finally:
                db.close()

        scope.setdefault("state", {})
        scope["state"]["experiments"] = experiment_assignments
        token = _experiment_context.set(experiment_assignments)

        async def send_with_headers(message):
            if message["type"] == "http.response.start" and experiment_assignments:
                headers = dict(message.get("headers", []))
                exp_header = ",".join(f"{e}:{v}" for e, v in experiment_assignments.items())
                headers[b"x-experiments"] = exp_header.encode()
                message = {**message, "headers": list(headers.items())}
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        finally:
            _experiment_context.reset(token)