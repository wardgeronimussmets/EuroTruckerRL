from enum import Enum
class RightLeftHandDriveType(Enum):
    LEFT = 1, 
    RIGHT = 2,
    NONE = 0

class ImageSimilarityMatch(Enum):
    NO_MATCH = 0,
    FERRY = 1,
    INFO = 2,
    PARKING_LOT = 3,
    FUEL_STOP = 4
    
class RequestedLightMode(Enum):
    OFF  = 0,
    PARKING = 1,
    ON = 2,
    HIGH_BEAMS = 3

class CurrentLightMode(Enum):
    OFF = 0,
    PARKING = 1,
    ON = 2