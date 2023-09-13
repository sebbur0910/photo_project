@validates("line_colour")
    def validate_background_colour(self, key, address):
        if not re.fullmatch("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", address):
            raise ValueError("Line colour must be in hex colour code format")
        return address

    @validates("default_border_colour")
    def validate_background_colour(self, key, address):
        if not re.fullmatch("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", address):
            raise ValueError("Default border colour must be in hex colour code format")
        return address