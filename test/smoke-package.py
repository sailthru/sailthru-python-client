"""Exercise the installed library using a loopback server and fake credentials."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import sys
from threading import Thread
from urllib.parse import parse_qs

import sailthru
from sailthru import SailthruClient


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    installed_path = Path(sailthru.__file__).resolve()
    check(installed_path.is_relative_to(Path(sys.prefix).resolve()),
          f"Client loaded outside the isolated installation: {installed_path}")
    failures = []
    user = {"id": "smoke@example.com"}
    response = {"ok": True}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                check(self.path == "/user", "Expected the /user endpoint")
                body = self.rfile.read(int(self.headers["Content-Length"]))
                params = parse_qs(body.decode("utf-8"))
                check(params["api_key"] == ["smoke-key"], "API key was not preserved")
                check(params["format"] == ["json"], "Expected the JSON response format")
                check(json.loads(params["json"][0]) == user, "User payload was not preserved")
                check(re.fullmatch(r"[a-f0-9]{32}", params["sig"][0]),
                      "Missing or malformed signature")

                encoded = json.dumps(response).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
            except Exception as error:
                failures.append(error)
                self.send_error(500, "Smoke request validation failed")

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = SailthruClient("smoke-key", "smoke-secret",
                              api_url=f"http://127.0.0.1:{server.server_port}", request_timeout=5)
        result = client.api_post("user", user)
        if failures:
            raise AssertionError("Local server rejected the client request") from failures[0]
        check(result.get_status_code() == 200, "Expected a successful HTTP response")
        check(result.is_ok(), "Client reported an unsuccessful response")
        check(result.get_body() == response, "Client did not parse the expected response")
        print("Packaged client imported and completed a local API request.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
