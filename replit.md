kind = "api"
previewPath = "/"
title = "Chess AI Engine"
version = "1.0.0"
id = "3B4_FFSkEVBkAeYMFRJ2e"

[[services]]
localPort = 8082
name = "Chess AI Engine"
paths = ["/"]

[services.development]
run = "python3 -m http.server 8082 --directory /home/runner/workspace/artifacts/api-server/public"

[services.production]
serve = "static"
publicDir = "artifacts/api-server/public"
