def compute_cossim(a, b, eps=1e-8):
    from torch import Tensor, mm

    assert isinstance(a, Tensor)
    assert isinstance(b, Tensor)

    N = a.size(0),
    a = a.view(N, -1)
    a_denom = a.norm(dim=1, keepdim=True)
    a_norm = a / (a_denom + eps)
    del a, a_denom

    M = b.size(0)
    b = b.view(M, -1)
    b_denom = b.norm(dim=1, keepdim=True)
    b_norm = b / (b_denom + eps)
    del b, b_denom

    return mm(a_norm, b_norm.T)
