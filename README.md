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
