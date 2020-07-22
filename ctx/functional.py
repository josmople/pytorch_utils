from . import values as V

vfn = V.LambdaValue
vconst = V.ConstValue
vglobal = V.GlobalValue
vitem = V.ProxyItemValue
vattr = V.ProxyAttrValue

del V
