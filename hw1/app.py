from typing import Any, Awaitable, Callable
import json


async def application(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
):
    """
    Args:
        scope: Словарь с информацией о запросе
        receive: Корутина для получения сообщений от клиента
        send: Корутина для отправки сообщений клиенту
    """
    # TODO: Ваша реализация здесь
    path = scope["path"]
    method = scope["method"]
    query = scope.get("query_string", "").decode()

    body = ""
    if method == "POST":
        message = await receive()
        body = message.get("body", "")

    params = {}
    for pair in query.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = v

    async def sendJson(status: int, data: dict):
        body = json.dumps(data).encode()
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [("content-type", "application/json")],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })

    if path == "/factorial":
        nRaw = params.get("n")
        if nRaw is None:
            await sendJson(422, {})
            return
        try:
            n = int(nRaw)
        except ValueError:
            await sendJson(422, {})
            return
        if n < 0:
            await sendJson(400, {})
            return
        result = 1
        for i in range(2, n + 1):
            result *= i
        await sendJson(200, {"result": result})
        return

    if path.startswith("/fibonacci"):
        tail = path[len("/fibonacci"):]
        if not tail.startswith("/"):
            await sendJson(404, {})
            return
        nRaw = tail[1:]
        try:
            n = int(nRaw)
        except ValueError:
            await sendJson(422, {})
            return
        if n < 0:
            await sendJson(400, {})
            return
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        await sendJson(200, {"result": a})
        return

    if path == "/mean":
        try:
            data = json.loads(body) if body else None
        except Exception:
            await sendJson(400, {})
            return
        if not isinstance(data, list) or len(data) == 0:
            await sendJson(400, {})
            return
        try:
            result = sum(data) / len(data)
        except TypeError:
            await sendJson(400, {})
            return
        await sendJson(200, {"result": result})
        return

    await sendJson(404, {})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:application", host="0.0.0.0", port=8000, reload=True)
