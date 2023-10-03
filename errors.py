class DatasetExistsError(Exception):
    """Raised when attempting to create a dataset that already exists."""
    pass


class TableExistsError(Exception):
    """Raised when attempting to create a Table that already exists."""

    def __init__(self, table_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_id = table_id


class GraphQLQueryError(Exception):
    """Raised when a GraphQL query does not return a 200 response code."""

    def __init__(self, status_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status_code


class BulkOperationError(Exception):
    """Raised when the bulk operation run query returns an error."""

    def __init__(self, error_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_code = error_code
