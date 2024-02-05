import re
from unicodedata import normalize


def convertir_nombre_modelo(cadena):

    cadena = cadena.replace(' ', '').replace('_', '')
    # -> NFD y eliminar diacríticos
    cadena = re.sub(
            r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
            normalize( "NFD", cadena), 0, re.I
        )

    # -> NFC
    cadena = normalize( 'NFC', cadena)

    return cadena