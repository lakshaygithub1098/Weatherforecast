import socket

def check_port(port):
    s = socket.socket()
    result = s.connect_ex(('127.0.0.1', port))
    s.close()
    return "OPEN" if result == 0 else "CLOSED"

print(f'Backend (8000): {check_port(8000)}')
print(f'Frontend (5173): {check_port(5173)}')
print(f'Frontend (5174): {check_port(5174)}')
