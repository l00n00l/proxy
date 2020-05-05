# proxy
a simple proxy



# 使用方法
在本机运行
python client.py 服务器ip 服务器端口 [-P 本机开放端口]
···
usage: client.py [-h] [-P PORT] server_host server_port

sock5 proxy

positional arguments:
  server_host           server host
  server_port           server port

optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  listen port default:1080
···
在服务器运行
python server -P port
···
usage: server.py [-h] [-P PORT]

sock5 proxy

optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  listen port default:8888
···
# 生成密钥(文件名必须是en.json)
···
usage: gen_encryto_box.py [-h] count filename

make encryto box

positional arguments:
  count       box count.default:1000
  filename    target file name.default:encryto.json

optional arguments:
  -h, --help  show this help message and exit
···
