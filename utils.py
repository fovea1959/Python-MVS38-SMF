import json

class Only1Error(KeyError):
    pass

class Only1Dict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise Only1Error(f"Key '{key}' already exists and cannot be replaced.")
        super().__setitem__(key, value)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        # Handle custom objects by converting them to a dictionary
        if isinstance(o, (bytes, bytearray)):
            return o.hex()

        # Fallback to the base class encoder for default types or raising TypeError
        return super().default(o)

def write_list_of_bytes(filename: str, lob: list[bytes|bytearray]):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(lob, file, indent=1, cls=CustomJSONEncoder)

def read_list_of_bytes(filename: str) -> list[bytes|bytearray]:
    with open(filename, "r", encoding="utf-8") as file:
        scratch = json.load(file)
    rv = list()
    for s in scratch:
        rv.append(bytearray.fromhex(s))
    return rv