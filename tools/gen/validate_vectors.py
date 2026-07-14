#!/usr/bin/env python3
"""Validate specs/testvectors chống lại specs/schemas (nền của TEL-01)."""
import json, sys, glob, os
try:
    import jsonschema
except ImportError:
    sys.exit("pip install jsonschema")
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
schema = json.load(open(os.path.join(root, "specs/schemas/telemetry.schema.json")))
ok = True
for f in glob.glob(os.path.join(root, "specs/testvectors/valid/*.json")):
    try: jsonschema.validate(json.load(open(f)), schema)
    except Exception as e: ok = False; print(f"FAIL (phải valid): {f}: {e}")
for f in glob.glob(os.path.join(root, "specs/testvectors/invalid/*.json")):
    try:
        jsonschema.validate(json.load(open(f)), schema)
        ok = False; print(f"FAIL (phải invalid mà pass): {f}")
    except Exception: pass
print("testvectors: OK" if ok else "testvectors: FAIL"); sys.exit(0 if ok else 1)
