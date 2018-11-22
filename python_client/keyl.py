import websocket
ws = websocket.WebSocket()
ws.connect("ws://localhost", http_proxy_host="proxy_host_name", http_proxy_port=3000)