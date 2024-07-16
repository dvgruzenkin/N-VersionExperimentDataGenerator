from enum import Enum, auto

class MenuItem(Enum):
    ADD_MODULE = auto()
    LOAD_MODULE_LIST = auto()
    SAVE_MODULE = auto()
    SHOW_MODULES_LIST = auto()
    SET_CURRENT_MODULE = auto()
    SHOW_CURRENT_MODULE = auto()
    ADD_VERSIONS = auto()
    LOAD_MODULE_WITH_VERSIONS = auto()
    SAVE_MODULE_WITH_VERSIONS = auto()
    SHOW_MODULE_VERSIONS = auto()
    GENERATE_EXPERIMENT_DATA = auto()
    SAVE_EXPERIMENT_DATA = auto()
    LOAD_EXPERIMENT_DATA = auto()
    ADD_VOTE_ALGORITHM = auto()
    LOAD_VOTE_ALGORITHMS = auto()
    SAVE_VOTE_ALGORITHMS = auto()
    SHOW_VOTE_ALGORITHMS = auto()
    RUN_VOTE_ALGORITHMS = auto()
    MAKE_EXPERIMENT_ANALYSIS = auto()
    EXIT = 0
