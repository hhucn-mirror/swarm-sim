from enum import Enum


class FlockMemberType(Enum):
    """
    Enum to distinguish between flock member types.
    """
    Leader = 0
    Follower = 1


class FlockMode(Enum):
    """
    Enum to distinguish current flock mode.
    """
    Searching = 0,
    QueryingLocation = 1,
    FoundLocation = 2
    Flocking = 3,
    Dispersing = 4,
    Regrouping = 5,
    Optimizing = 6
