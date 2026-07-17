from enum import StrEnum


class ResearchType(StrEnum):
    HYPOTHESIS_TEST = "Hypothesis Test"
    EXPLORATORY = "Exploratory"
    COMPARATIVE = "Comparative"
    OPTIMIZATION = "Optimization"


class ResearchStatus(StrEnum):
    NEW = "NEW"
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class HypothesisStatus(StrEnum):
    NEW = "NEW"
    TESTING = "TESTING"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"


class ExperimentStatus(StrEnum):
    NEW = "NEW"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"