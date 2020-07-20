from enum import Enum


class FlockMemberType(Enum):
    Leader = 0
    Follower = 1


class FlockMode(Enum):
    Searching = 0,
    QueryingLocation = 1,
    FoundLocation = 2
    Flocking = 3,
    Dispersing = 4,
    Regrouping = 5,
    Optimizing = 6
