from dataclasses import dataclass

from factory_planner.loader.schema import Recipe


@dataclass(frozen=True)
class SupplyChain:
  recipe_id: str
  recipe: Recipe
  dependencies: dict[str, tuple[int, 'SupplyChain']]

  @property
  def total_time(self) -> float | None:
    if self.recipe.time is None:
      return None

    r = 0
    for n, i in self.dependencies.values():
      t = i.total_time
      if t is None:
        return None
      r += t
    return r + self.recipe.time

  def __mul__(self, other: int) -> 'SupplyChain':
    return SupplyChain(
        recipe_id=self.recipe_id,
        recipe=self.recipe,
        dependencies={k: (v * other, i) for k, (v, i) in self.dependencies.items()},
    )

@dataclass(frozen=True)
class SupplyChainCandidates:
  recipe_id: str
  recipe: Recipe

  dependencies: dict[str, list['SupplyChainCandidates']]
