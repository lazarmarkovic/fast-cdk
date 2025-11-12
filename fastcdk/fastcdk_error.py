import traceback

class FcdkError(Exception):
    def __init__(self, file_path: str, line: int | None, msg: str, cause: Exception | None = None):
        self.file_path = file_path
        self.line = line
        self.msg = msg
        # store the short message once
        self._text = f"{file_path}:{line}: {msg}" if line is not None else f"{file_path}: {msg}"
        super().__init__(self._text)
        self.cause = cause
        self.__cause__ = cause  # links it for traceback display

    def __str__(self) -> str:
        """when printed or logged explicitly"""
        return self._text

    def __repr__(self) -> str:
        """shown in debugger etc."""
        return f"FcdkError({self._text!r})"