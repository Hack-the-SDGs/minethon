"""Internal bridge utilities."""


def _extract_js_stack(exc: BaseException) -> str | None:
    """Try to extract a JS stack trace from a JSPyBridge exception.

    JSPyBridge exceptions may carry a ``stack`` attribute with the
    JavaScript stack trace string.
    """
    stack = getattr(exc, "stack", None)
    if isinstance(stack, str):
        return stack
    cause = exc.__cause__
    if cause is not None:
        stack = getattr(cause, "stack", None)
        if isinstance(stack, str):
            return stack
    return None
