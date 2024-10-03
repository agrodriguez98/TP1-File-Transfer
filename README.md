# TP1-File-Transfer

## Interfaz
### Cliente upload
```
> python upload.py -h
usage : upload.py [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]
< command description >
optional arguments :
    -h , -- help        show this help message and exit
    -v , -- verbose     increase output verbosity
    -q , -- quiet       decrease output verbosity
    -H , -- host        server IP address
    -p , -- port        server port
    -s , -- src         source file path
    -n , -- name        file name
    -sr, -- modesr      defines if the mode is stop & wait or selective repeat (default: stop & wait)
```
### Cliente download
```
> python download.py -h
usage : download.py [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]
< command description >
optional arguments :
    -h , -- help    show this help message and exit
    -v , -- verbose increase output verbosity
    -q , -- quiet   decrease output verbosity
    -H , -- host    server IP address
    -p , -- port    server port
    -d , -- dst     destination file path
    -n , -- name    file name
    -sr, -- modesr      defines if the mode is stop & wait or selective repeat (default: stop & wait)
```
### Server
```
> python start-server.py -h
usage : start-server.py [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s DIRPATH ]
< command description >
optional arguments :
    -h , -- help
    show this help message and exit
    -v , -- verbose     increase output verbosity
    -q , -- quiet       decrease output verbosity
    -H , -- host        service IP address (default: localhost)
    -p , -- port        service port (default: 12000)
    -s , -- storage     storage dir path (default: ./server_storage)
    -sr, -- modesr      defines if the mode is stop & wait or selective repeat (default: stop & wait)
```