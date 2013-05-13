import struct

def deep_asdict(o):
    if isinstance(o, dict):
        return dict( (k, deep_asdict(v)) for (k,v) in o.items() )
    elif isinstance(o, list):
        return map(deep_asdict, o)
    elif hasattr(o, '_asdict'):
        return dict( (k, deep_asdict(v)) for (k,v) in o._asdict().items() )
    else:
        return o

_REGISTER_TYPES = {
    1: 'h',     # Signed short
    2: 'i',     # Signed int
    4: 'q',     # Signed long long
}

def unpack_values(values):
    '''Unpacks the given values into a single value.

    :param values: is a list of 16-bit unsigned integers.
    :return: the result of concatenating the list of unsigned integers, and
             reading the whole as a big-endian  2's complement value (of the
             approprate width) 
    '''
    value_bytes = ''.join( struct.pack('>H', v) for v in values )
    return_type = _REGISTER_TYPES[len(values)]

    return struct.unpack('>' + return_type,
                         value_bytes)[0]

def pack_value(value, width):
    '''Pack the given value as a list of 16-bit unsigned shorts.'''
    value_type = _REGISTER_TYPES[width]
    byte_string = struct.pack('>' + value_type, value)

    return [ struct.unpack('>H', byte_string[2*i : 2*i+2])[0] \
                    for i in xrange(width) ]
