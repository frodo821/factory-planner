from os.path import join, dirname, abspath
from pathlib import Path
from types import MappingProxyType
from factory_planner.loader import Loader
from factory_planner.simulator.supply_chain import SupplyChainCandidates


class Satisfactory:

  def __init__(self):
    self._loader = Loader()
    self._loader.load_dir(abspath(join(dirname(__file__), '..', '..', 'satisfactory')))
    self._loader.validate()

  def load_custom_definition_file(self, path: str | Path):
    self._loader.load(path)
    self._loader.validate()

  def load_custom_definition_directory(self, path: str | Path):
    self._loader.load_dir(path)
    self._loader.validate()

  @property
  def recipes(self):
    return MappingProxyType(self._loader.recipes)

  @property
  def items(self):
    return MappingProxyType(self._loader.items)

  @property
  def facilities(self):
    return MappingProxyType(self._loader.facilities)

  def lookup_item_supply_chain(self, itemId: str, maximum_depth=20) -> list[SupplyChainCandidates]:
    if maximum_depth <= 0:
      return []

    candidates = self._loader.reverse_recipes.get(itemId, [])

    if len(candidates) == 0:
      return []

    return [
        SupplyChainCandidates(
            recipe_id=i,
            recipe=(r := self._loader.recipes[i]),
            dependencies={k.type: self.lookup_item_supply_chain(k.type, maximum_depth=maximum_depth - 1)
                          for k in r.ingredients},
        ) for i in candidates
    ]
