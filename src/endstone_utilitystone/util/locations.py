from __future__ import annotations

from endstone.level import Location


def encodeLocation(location: Location) -> dict:
    return {
        "dimension": location.dimension.name,
        "x": round(location.x, 3),
        "y": round(location.y, 3),
        "z": round(location.z, 3),
        "pitch": round(location.pitch, 2),
        "yaw": round(location.yaw, 2),
    }


def decodeLocation(server, payload) -> Location | None:
    if not isinstance(payload, dict):
        return None

    dimensionName = payload.get("dimension")
    if not dimensionName:
        return None

    try:
        dimension = server.level.get_dimension(str(dimensionName))
    except Exception:
        return None

    if dimension is None:
        return None

    try:
        return Location(
            dimension,
            float(payload["x"]),
            float(payload["y"]),
            float(payload["z"]),
            float(payload.get("pitch", 0.0)),
            float(payload.get("yaw", 0.0)),
        )
    except (KeyError, TypeError, ValueError):
        return None


def describeLocation(location: Location) -> str:
    return f"{location.dimension.name} {location.block_x}, {location.block_y}, {location.block_z}"


def flatDistanceSquared(first: Location, second: Location) -> float:
    deltaX = first.x - second.x
    deltaY = first.y - second.y
    deltaZ = first.z - second.z
    return deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ
