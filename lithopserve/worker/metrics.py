from dataclasses import dataclass
from typing import Optional


# Base class for all metrics
@dataclass
class MetricBase:
    __slots__ = ['timestamp', 'collection_id']

    timestamp: float
    collection_id: int

    def __post_init__(self):
        if not hasattr(self, 'METRIC_TYPES_FIELDS'):
            raise AttributeError(f"{self.__class__.__name__} must define 'METRIC_TYPES_FIELDS'.")

    def __lt__(self, other):
        if not isinstance(other, MetricBase):
            return NotImplemented
        return self.timestamp < other.timestamp

    # Add two metrics of the same type
    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Cannot add different metric types: {type(self).__name__} and {type(other).__name__}"
            )
        new_data = {"timestamp": max(self.timestamp, other.timestamp), "collection_id": self.collection_id}
        for field_name in self.METRIC_TYPES_FIELDS:
            new_data[field_name] = getattr(self, field_name, 0) + getattr(other, field_name, 0)
        return self.__class__(**new_data)

    # Subtract two metrics of the same type
    def __sub__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Cannot subtract different metric types: {type(self).__name__} and {type(other).__name__}"
            )
        new_data = {"timestamp": max(self.timestamp, other.timestamp), "collection_id": self.collection_id}
        for field_name in self.METRIC_TYPES_FIELDS:
            new_data[field_name] = getattr(self, field_name, 0) - getattr(other, field_name, 0)
        return self.__class__(**new_data)

    # Divide metric by a scalar to get average
    def __truediv__(self, number):
        if not isinstance(number, (int, float)):
            return NotImplemented
        if number == 0:
            raise ValueError("Cannot divide by zero.")
        new_data = {"timestamp": self.timestamp, "collection_id": self.collection_id}
        for field_name in self.METRIC_TYPES_FIELDS:
            new_data[field_name] = getattr(self, field_name, 0) / number
        return self.__class__(**new_data)


# Base class for metrics associated with processes
@dataclass
class ProcessMetric(MetricBase):
    __slots__ = ['pid', 'parent_pid']

    pid: Optional[int]
    parent_pid: Optional[int]


# CPU metrics for processes
@dataclass
class CPUMetric(ProcessMetric):
    __slots__ = ['cpu_usage', 'user_time', 'system_time', 'children_user_time', 'children_system_time', 'iowait_time']

    cpu_usage: float
    user_time: float
    system_time: float
    children_user_time: float
    children_system_time: float
    iowait_time: float

    METRIC_TYPES_FIELDS = [
        'cpu_usage', 'user_time', 'system_time',
        'children_user_time', 'children_system_time', 'iowait_time'
    ]


# Memory metrics for processes
@dataclass
class MemoryMetric(ProcessMetric):
    __slots__ = ['memory_usage']

    memory_usage: float

    METRIC_TYPES_FIELDS = ['memory_usage']


# Disk metrics for processes
@dataclass
class DiskMetric(ProcessMetric):
    __slots__ = ['disk_read_mb', 'disk_write_mb', 'disk_read_rate', 'disk_write_rate']

    disk_read_mb: float
    disk_write_mb: float
    disk_read_rate: float
    disk_write_rate: float

    METRIC_TYPES_FIELDS = [
        'disk_read_mb', 'disk_write_mb', 'disk_read_rate', 'disk_write_rate'
    ]


# Network metrics for the system (not process-specific)
@dataclass
class NetworkMetric(MetricBase):
    __slots__ = ['net_read_mb', 'net_write_mb', 'net_read_rate', 'net_write_rate']

    net_read_mb: float
    net_write_mb: float
    net_read_rate: float
    net_write_rate: float

    METRIC_TYPES_FIELDS = [
        'net_read_mb', 'net_write_mb', 'net_read_rate', 'net_write_rate'
    ]
