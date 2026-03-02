class DomainCategoryAlreadyExistsError(Exception):
    def __init__(self, domain: str, category_id: int):
        self.domain = domain
        self.category_id = category_id
        super().__init__(f"Domain '{domain}' is already mapped to category_id={category_id}")


class DomainCategoryNotFoundError(Exception):
    def __init__(self, identifier):
        super().__init__(f"Domain category not found: {identifier}")

