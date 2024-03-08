# RDT 3.0

1. Start server.py > `python server.py`
2. Start the clients > `python client.py`

Make sure that the files you desire to send are placed in the `samples` folder before running te clients. We use `os.listdir` to read the directory's files.

## Observations

- You can change the parameters that configure the timeout and maximum buffer size by modifing the following:
      - `MAX_BUFF_SIZE`
      - `CLIENT_TIMEOUT` (on the client `request_pkt` fn)
      - `SERVER_TIMOUT` (when instanciating the server)

- The server was built to never stop running unless it crashes (closing the terminal or trying to connect when the socket is closed).

## Team

- Leonidas Netto (ldcn)
- Matheus Boncsidai (mjbo)
- Mikael Cavalcanti (mcs11)
- Murilo Barbosa (mbn2)
- Renato Ferraz (rnfo)
- Victoria Luquet Tewari (vllst)
