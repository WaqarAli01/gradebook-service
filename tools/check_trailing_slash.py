import http.client, http.server, sys, threading
import gradebook

gradebook.STATE = {
    "students": {"S1": {"id": "S1", "name": "Ayesha", "joined": "2026-01-01"}},
    "assessments": {},
    "marks": [],
}
server = http.server.HTTPServer(("127.0.0.1", 0), gradebook.Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
connection.request("GET", "/students/S1/")
status = connection.getresponse().status
print("GET /students/S1/ ->", status)
sys.exit(0 if status == 200 else 1)