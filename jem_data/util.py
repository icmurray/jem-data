def deep_asdict(o):
    if isinstance(o, dict):
        return dict( (k, deep_asdict(v)) for (k,v) in o.items() )
    elif hasattr(o, '_asdict'):
        return dict( (k, deep_asdict(v)) for (k,v) in o._asdict().items() )
    else:
        return o

