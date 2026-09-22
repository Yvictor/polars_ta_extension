"""Extract the batch API from the pinned upstream headers and shared library.

Usage: python scripts/extract_api.py /path/to/ta-lib-0.8.1 /path/to/libta-lib.so
Only maintainers regenerating the checked-in API manifest need a shared library.
"""
import ctypes as C
import json
import re
import sys
from pathlib import Path

class FuncInfo(C.Structure):
    _fields_ = [(n, C.c_char_p) for n in ('name', 'group', 'hint')] + [
        ('flags', C.c_int), ('nbInput', C.c_uint), ('nbOptInput', C.c_uint),
        ('nbOutput', C.c_uint), ('handle', C.c_void_p)]

class OptInfo(C.Structure):
    _fields_ = [('type', C.c_int), ('paramName', C.c_char_p), ('flags', C.c_int),
                ('displayName', C.c_char_p), ('dataSet', C.c_void_p),
                ('defaultValue', C.c_double), ('hint', C.c_char_p), ('helpFile', C.c_char_p)]

def main():
    source, library = sys.argv[1:]
    lib = C.CDLL(library)
    lib.TA_GetVersionString.restype = C.c_char_p
    assert lib.TA_GetVersionString().decode().startswith('0.8.1 ')
    assert lib.TA_Initialize() == 0
    header = (Path(source) / 'include/ta_func.h').read_text()
    header = re.sub(r'/\*.*?\*/', '', header, flags=re.S)
    functions = []
    for name, args in re.findall(r'TA_RetCode TA_([A-Z0-9_]+)\(\s*int\s+startIdx,(.*?)\);', header, re.S):
        if name.startswith('S_'):
            continue
        handle = C.c_void_p()
        assert lib.TA_GetFuncHandle(name.encode(), C.byref(handle)) == 0
        info = C.POINTER(FuncInfo)()
        assert lib.TA_GetFuncInfo(handle, C.byref(info)) == 0
        params = []
        for i in range(info.contents.nbOptInput):
            opt = C.POINTER(OptInfo)()
            assert lib.TA_GetOptInputParameterInfo(handle, i, C.byref(opt)) == 0
            p = opt.contents
            raw = p.paramName.decode()
            ctype = re.search(r'(int|double|TA_MAType)\s+' + raw + r'\b', args)[1]
            default = p.defaultValue if ctype == 'double' else int(p.defaultValue)
            params.append(dict(name=raw[5:].lower(), c_name=raw, type=ctype, default=default))
        inputs = re.findall(r'const double\s+in(\w+)\[\]', args)
        outputs = re.findall(r'(double|int)\s+out(\w+)\[\]', args)
        assert inputs and outputs, name
        functions.append(dict(name=name.lower(), group=info.contents.group.decode(),
            description=info.contents.hint.decode(), inputs=[n.lower() for n in inputs],
            params=params, outputs=[dict(name=n.lower(), type=t) for t,n in outputs]))
    Path('scripts/api.json').write_text(json.dumps(functions, indent=2)+'\n')
    print(f'{len(functions)} batch indicators extracted')

if __name__ == '__main__':
    main()
