from dataclasses import dataclass
from typing import Literal, NotRequired, Required, TypedDict, TypeAlias


@dataclass(frozen=True)
class Item:
  name: str
  stack_size: int
  type: Literal['solid', 'fluid'] = 'solid'


class ItemDict(TypedDict):
  name: Required[str]
  stack_size: Required[int]
  type: Literal['solid', 'fluid']


@dataclass(frozen=True)
class Facility:
  type: Literal['storage', 'constructor']
  name: str


@dataclass(frozen=True)
class Storage(Facility):
  slots: int


class StorageDict(TypedDict):
  type: Literal['storage']
  name: Required[str]
  slots: Required[int]


@dataclass(frozen=True)
class Constructor(Facility):
  production_rate: float = 1.0
  required_power: float = 0.0


class ConstructorDict(TypedDict):
  type: Literal['constructor']
  name: Required[str]
  production_rate: Required[float]
  required_power: Required[float]


FacilityDict: TypeAlias = StorageDict | ConstructorDict


@dataclass(frozen=True)
class ItemIO:
  type: str
  per_minute: float
  per_cycle: float | None = None

  @property
  def minutes_per_cycle(self) -> float | None:
    if self.per_cycle is None:
      return None
    return self.per_minute / self.per_cycle

  @property
  def seconds_per_cycle(self) -> float | None:
    if self.per_cycle is None:
      return None
    return (self.per_minute * 60.0) / self.per_cycle


class ItemIODict(TypedDict):
  type: Required[str]
  per_minute: Required[float]
  per_cycle: Required[float]


@dataclass(frozen=True)
class Recipe:
  ingredients: list[ItemIO]
  outputs: list[ItemIO]
  allowed_facilities: list[str]
  required_power: float = 0.0
  name: str = ''
  time: float = 0.0


class RecipeDict(TypedDict):
  ingredients: Required[list[ItemIODict]]
  outputs: Required[list[ItemIODict]]
  allowed_facilities: Required[list[str]]
  required_power: Required[float]
  name: Required[str]
  time: Required[float]


@dataclass(frozen=True)
class FactoryNode:
  type: str
  incoming: list[str]
  outgoing: list[str]
  recipe: Recipe | None = None
  production_rate: float | None = None


class FactoryNodeDict(TypedDict):
  type: Required[str]
  incoming: Required[list[str]]
  outgoing: Required[list[str]]
  recipe: NotRequired[RecipeDict]
  production_rate: NotRequired[float]


@dataclass(frozen=True)
class Factory:
  sources: dict[str, ItemIO]
  sinks: dict[str, ItemIO]
  nodes: dict[str, FactoryNode]


class FactoryDict(TypedDict):
  sources: Required[dict[str, ItemIODict]]
  sinks: Required[dict[str, ItemIODict]]
  nodes: Required[dict[str, FactoryNodeDict]]


class DocumentDict(TypedDict):
  items: NotRequired[dict[str, ItemDict]]
  facilities: NotRequired[dict[str, FacilityDict]]
  recipes: NotRequired[dict[str, RecipeDict]]
  factory: NotRequired[FactoryDict]
