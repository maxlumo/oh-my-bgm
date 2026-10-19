"""Read-only static server for a review folder, with HTTP Range support (iOS Safari needs it
to play and seek audio). No directory listings. Stdlib only.

usage: python3 serve.py DIR [port]        (default port 8766, binds 0.0.0.0)
"""
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path.cwd()


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mp3": "audio/mpeg",
                      ".wav": "audio/wav", ".md": "text/plain; charset=utf-8"}

    def list_directory(self, path):  # no directory listings
        self.send_error(404)
        return None

    def send_head(self):
        path = Path(self.translate_path(self.path))
        rng = self.headers.get("Range")
        if not rng or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        try:
            unit, spec = rng.split("=", 1)
            a, b = spec.split(",")[0].strip().split("-")
            start = int(a) if a else size - int(b)
            end = int(b) if a and b else size - 1
        except ValueError:
            start, end = 0, size - 1
        if unit.strip() != "bytes" or start >= size or start < 0:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return None
        end = min(end, size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        n = getattr(self, "_remaining", None)
        if n is None:
            return super().copyfile(source, outputfile)
        while n > 0:
            chunk = source.read(min(65536, n))
            if not chunk:
                break
            outputfile.write(chunk)
            n -= len(chunk)

    def end_headers(self):
        if not self.headers.get("Range"):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()


if __name__ == "__main__":
    ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    port = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PORT", 8766))
    srv = ThreadingHTTPServer(("0.0.0.0", port), partial(Handler, directory=str(ROOT)))
    print(f"serving {ROOT} on http://0.0.0.0:{port}/", flush=True)
    srv.serve_forever()
