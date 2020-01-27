def module_param_grad(module, requires_grad=False):
    from torch.nn import Module
    assert isinstance(module, Module)
    for p in module.parameters():
        p.requires_grad_(requires_grad)
    return module


def freeze_module(module):
    return module_param_grad(module, False)


def unfreeze_module(module):
    return module_param_grad(module, True)
