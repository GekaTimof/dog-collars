# получить токен из запроса
def get_arg_from_request(kwargs, arg: str):
    value = 0
    for key in [*kwargs]:
        if hasattr(kwargs[key], arg):
            value = getattr(kwargs[key], arg)

    return value