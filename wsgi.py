import os, dotenv
from app import create_app

dotenv.load_dotenv()

app = create_app()

server_port = os.environ.get("SERVER_PORT") # int type allowed
server_host = os.environ.get("SERVER_HOST") # string type

if __name__ == '__main__':
    app.run(host=server_host, port=server_port)