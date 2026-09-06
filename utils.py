class Only1Error(KeyError):
    pass

class Only1Dict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise Only1Error(f"Key '{key}' already exists and cannot be replaced.")
        super().__setitem__(key, value)