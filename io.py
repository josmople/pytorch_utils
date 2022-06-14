def state_dicts(obj: object):
    state_dict_provider = getattr(obj, "state_dict", None)
    if callable(state_dict_provider):
        return state_dict_provider()

    state_dict = {}
    for prop_name in dir(obj):
        prop_value = getattr(obj, prop_name, None)
        state_dict_provider = getattr(prop_value, "state_dict", None)
        if callable(state_dict_provider):
            prop_state = state_dict_provider()
            state_dict[prop_name] = prop_state
    return state_dict


def load_state_dicts(obj: object, state_dict: dict):
    state_dict_consumer = getattr(obj, "load_state_dict", None)
    if callable(state_dict_consumer):
        state_dict_consumer(state_dict)
        return

    for prop_name in state_dict:
        prop_state = state_dict[prop_name]
        prop_value = getattr(obj, prop_name, None)
        state_dict_consumer = getattr(prop_value, "load_state_dict", None)
        if callable(state_dict_consumer):
            state_dict_consumer(prop_state)
