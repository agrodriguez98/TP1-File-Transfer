# TP1-File-Transfer

Esto se puede poner en el informe:

## Formato del protocolo

    FILE message
    | P | TYPE | FILENAME |
    | 1 |  4   |    8     |

    DOWN message
    | P | TYPE | FILENAME |
    | 1 |  4   |    8     |
    
    DONE message
    | P | TYPE |
    | 1 |  4   |
    
    ACK message
    | P | TYPE |
    | 1 |  4   |
    
    DATA message
    | P | TYPE |  PAYLOAD  |
    | 1 |  4   |   4096    |
