#!/usr/bin/env python3
# ---------------------------------------------------------------------
# Source File: logagent.py
# Create Date: 09/19/2026 09:15
# Last Updated: 09/19/2026 09:15
# Author: Neal T. Bailey <nealbailey@hotmail.com>
#
# ----------------------------------------------------------------------
# GNU GENERAL PUBLIC LICENSE
# ----------------------------------------------------------------------
# Version 2, June 1991 
# Copyright (C) 1989, 1991 Free Software Foundation, Inc.  
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# https://www.gnu.org/licenses/gpl-2.0.html
#-----------------------------------------------------------------------
# Copyright (c) 2010-2015 Baileysoft Solutions
#-----------------------------------------------------------------------
import socket
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

from logreader import read_log

HOST = "0.0.0.0"
PORT = 8010
BUILD_VERSION = "1.7.1"  # increment on every change so clients can detect stale versions

CONFIG_FILE = Path(__file__).with_name("logagent.json")
with CONFIG_FILE.open(encoding="utf-8") as config_file:
    CONFIG = json.load(config_file)

LOGS = CONFIG["logs"]
LINE_LIMIT = CONFIG.get("settings", {}).get("line_limit", {})


def filter_log(contents: str, search: str) -> str:
    """Return log lines containing the search string (case-insensitive)."""
    search = search.lower()
    matches = [line for line in contents.splitlines() if search in line.lower()]
    return "\n".join(matches) if matches else "No matches found in log."


def limit_log(contents: str) -> str:
    """Return only the last N lines of the log, per the line_limit setting."""
    if not LINE_LIMIT.get("enabled"):
        return contents

    lines = contents.splitlines()
    limit = LINE_LIMIT.get("lines")

    return "\n".join(lines[-limit:]) if limit else contents


class LogAgentHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status_code=200):
        response = json.dumps(data, indent=2).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(response)

    def send_text(self, text, status_code=200):
        response = text.encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(response)

    def do_GET(self):

        request = urlsplit(self.path)
        path = unquote(request.path)
        search = parse_qs(request.query, keep_blank_values=True).get("search", [None])[0]

        # Remove leading/trailing slashes
        log_name = path.strip("/")
        
        # Return the list of available logs
        if log_name == "":
            self.send_json({
                "hostname": socket.gethostname(),
                "port": PORT,
                "build_version": BUILD_VERSION,
                "line_limit": LINE_LIMIT if LINE_LIMIT.get("enabled") else None,
                "logs": list(LOGS.keys())
            })
            return

        # /logname
        if log_name in LOGS:

            try:
                contents = read_log(LOGS[log_name])
                if search:
                    contents = filter_log(contents, search)
                else:
                    contents = limit_log(contents)

                self.send_text(contents)

            except FileNotFoundError:
                self.send_json({
                    "error": "Log file not found",
                    "log": log_name
                }, 404)

            except PermissionError:
                self.send_json({
                    "error": "Permission denied",
                    "log": log_name
                }, 403)

            except Exception as exc:
                self.send_json({
                    "error": "Unable to read log",
                    "log": log_name,
                    "details": str(exc)
                }, 500)

            return

        # Unknown endpoint
        self.send_json({
            "error": "Unknown log",
            "available_logs": list(LOGS.keys())
        }, 404)

    def log_message(self, format, *args):
        """
        Keep the standard HTTP server from printing every request.
        """
        return


def main():

    server = HTTPServer((HOST, PORT), LogAgentHandler)

    print(f"Log agent listening on {HOST}:{PORT} (build {BUILD_VERSION})")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping log agent...")

    finally:
        server.server_close()


if __name__ == "__main__":
    main()