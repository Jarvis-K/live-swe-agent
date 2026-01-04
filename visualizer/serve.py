#!/usr/bin/env python3
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

RESULTS_DIR = Path('/root/live-swe-agent/results')

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/issues.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            issues = [d.name for d in RESULTS_DIR.iterdir() if d.is_dir() and (d / f'{d.name}.traj.json').exists()]
            self.wfile.write(json.dumps(issues).encode())
        elif self.path.startswith('/trajectories/'):
            issue = self.path.split('/')[-1].replace('.traj.json', '')
            traj_file = RESULTS_DIR / issue / f'{issue}.traj.json'
            if traj_file.exists():
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(traj_file.read_bytes())
            else:
                self.send_error(404)
        else:
            super().do_GET()

os.chdir(Path(__file__).parent)
print('Server running at http://localhost:8000')
print('Open http://localhost:8000/visualizer.html in your browser')
HTTPServer(('', 8000), Handler).serve_forever()
