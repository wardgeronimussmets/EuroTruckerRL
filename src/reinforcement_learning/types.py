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