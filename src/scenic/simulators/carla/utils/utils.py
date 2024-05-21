import math

import carla
import scipy

from scenic.core.geometry import headingOfSegment, normalizeAngle
from scenic.core.vectors import Orientation, Vector


def _snapToGround(world, location, blueprint):
    """Mutates @location to have the same z-coordinate as the nearest waypoint in @world."""
    waypoint = world.get_map().get_waypoint(location)
    # patch to avoid the spawn error issue with vehicles and walkers.
    z_offset = 0
    if blueprint is not None and ("vehicle" in blueprint or "walker" in blueprint):
        z_offset = 0.5

    location.z = waypoint.transform.location.z + z_offset
    return location


def scenicToCarlaVector3D(x, y, z=0.0):
    # NOTE: Used for velocity, acceleration; superclass of carla.Location
    z = 0.0 if z is None else z
    return carla.Vector3D(x, -y, z)


def scenicToCarlaLocation(pos, world=None, blueprint=None, snapToGround=False):
    if snapToGround:
        assert world is not None
        return _snapToGround(world, carla.Location(pos.x, -pos.y, 0.0), blueprint)
    return carla.Location(pos.x, -pos.y, pos.z)


def scenicToCarlaRotation(orientation):
    origin = (0, 0, 0)
    scenic_y_axis = (0, 1, 0)
    obj_3d_heading = orientation.r.apply(scenic_y_axis)
    scenic_yaw = headingOfSegment(origin, obj_3d_heading)
    carla_yaw = -90 - math.degrees(scenic_yaw)
    return carla.Rotation(pitch=0, yaw=carla_yaw, roll=0)


def carlaToScenicPosition(loc):
    return Vector(loc.x, -loc.y, loc.z)


def carlaToScenicElevation(loc):
    return loc.z


def carlaToScenicOrientation(rot):
    angles = (-rot.yaw - 90, rot.pitch, rot.roll)
    r = scipy.spatial.transform.Rotation.from_euler(
        seq="ZXY", angles=angles, degrees=True
    )
    return Orientation(r)


def carlaToScenicHeading(rot):
    return normalizeAngle(-math.radians(rot.yaw + 90))


def carlaToScenicAngularSpeed(vel):
    return math.hypot(math.radians(vel.x), -math.radians(vel.y), math.radians(vel.y))


def carlaToScenicAngularVel(vel):
    return Vector(math.radians(vel.x), -math.radians(vel.y), math.radians(vel.y))


_scenicToCarlaMap = {
    "red": carla.TrafficLightState.Red,
    "green": carla.TrafficLightState.Green,
    "yellow": carla.TrafficLightState.Yellow,
    "off": carla.TrafficLightState.Off,
    "unknown": carla.TrafficLightState.Unknown,
}


def scenicToCarlaTrafficLightStatus(status):
    return _scenicToCarlaMap.get(status, None)


def carlaToScenicTrafficLightStatus(status):
    return str(status).lower()
