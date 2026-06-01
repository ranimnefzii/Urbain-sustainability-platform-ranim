from typing import Any, Dict


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    success: bool = True,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {"success": success, "message": message}
    if data is not None:
        result["data"] = data
    return result
