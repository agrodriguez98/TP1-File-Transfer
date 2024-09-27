# TP1-File-Transfer

Esto se puede poner en el informe:

## Formato del protocolo

    FILE message
    | P | TYPE | FLN_LEN | FILENAME |
    | 1 |  4   |    1    |    var   |

    DOWN message
    | P | TYPE | FLN_LEN | FILENAME |
    | 1 |  4   |    1    |    var   |
    
    DONE message
    | P | TYPE |
    | 1 |  4   |
    
    ACK message
    | P | TYPE |
    | 1 |  4   |
    
    DATA message
    | P | TYPE |  PAYLOAD  |
    | 1 |  4   |   4096    |


## Restricciones
El nombre del archivo no puede exceder de 255 bytes, dado que su longitud se almacena en 1 byte

## Interfaz
### Cliente upload
```
> python upload -h
usage : upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]
< command description >
optional arguments :
    -h , -- help        show this help message and exit
    -v , -- verbose     increase output verbosity
    -q , -- quiet       decrease output verbosity
    -H , -- host        server IP address
    -p , -- port        server port
    -s , -- src         source file path
    -n , -- name        file name
```
### Cliente download
```
> python download -h
usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]
< command description >
optional arguments :
    -h , -- help    show this help message and exit
    -v , -- verbose increase output verbosity
    -q , -- quiet   decrease output verbosity
    -H , -- host    server IP address
    -p , -- port    server port
    -d , -- dst     destination file path
    -n , -- name    file name
```
### Server
```
> python start - server -h
usage : start - server [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s DIRPATH ]
< command description >
optional arguments :
    -h , -- help
    show this help message and exit
    -v , -- verbose     increase output verbosity
    -q , -- quiet       decrease output verbosity
    -H , -- host        service IP address
    -p , -- port        service port
    -s , -- storage     storage dir path
```
