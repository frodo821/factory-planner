from pathlib import Path
from warnings import warn
from yaml import safe_load
from factory_planner.loader.schema import Constructor, DocumentDict, Facility, FacilityDict, Factory, FactoryDict, Item, ItemDict, ItemIO, Recipe, RecipeDict, Storage


class Loader:

  def __init__(self):
    self.items: dict[str, Item] = {}
    self.facilities: dict[str, Facility] = {}
    self.recipes: dict[str, Recipe] = {}
    self.reverse_recipes: dict[str, list[str]] = {}

  def load_dir(self, path: str | Path):
    for p in Path(path).glob('*.yaml'):
      self.load(p.absolute())

    for p in Path(path).glob('*.yml'):
      self.load(p.absolute())

  def load(self, path: str | Path):
    with open(path, 'r') as f:
      doc: DocumentDict = safe_load(f)

    if 'items' in doc:
      self._load_items(doc['items'])

    if 'facilities' in doc:
      self._load_facilities(doc['facilities'])

    if 'recipes' in doc:
      self._load_recipes(doc['recipes'])

  def _load_items(self, items: dict[str, ItemDict]):
    if not isinstance(items, dict):
      warn(f"invalid value for 'items': expected dict, got {type(items)}. skipping.")
      return

    for k, v in items.items():
      try:
        self.items[k] = Item(
            name=v.get('name', k),
            stack_size=v['stack_size'],
            type=v.get('type', 'solid'),
        )
      except KeyError as e:
        warn(f"invalid item '{k}' found: {e}")

  def _load_facilities(self, facilities: dict[str, FacilityDict]):
    if not isinstance(facilities, dict):
      warn(f"invalid value for 'facilities': expected dict, got {type(facilities)}. skipping.")
      return

    for k, v in facilities.items():
      try:
        if v['type'] == 'storage':
          self.facilities[k] = Storage(
              name=v.get('name', k),
              slots=v['slots'],
              type='storage',
          )
        elif v['type'] == 'constructor':
          self.facilities[k] = Constructor(
              name=v.get('name', k),
              production_rate=v.get('production_rate', 1.0),
              required_power=v.get('required_power', 0.0),
              type='constructor',
          )
        else:
          warn(f"invalid facility '{k}' found: invalid type '{v['type']}'. skipping.")
      except KeyError as e:
        warn(f"invalid facility '{k}' found: {e}")

  def _load_recipes(self, recipes: dict[str, RecipeDict]):
    if not isinstance(recipes, dict):
      warn(f"invalid value for 'recipes': expected dict, got {type(recipes)}. skipping.")
      return

    for k, v in recipes.items():
      try:
        ingredients = [ItemIO(
            type=i['type'],
            per_minute=i['per_minute'],
            per_cycle=i.get('per_cycle', None),
        ) for i in v['ingredients']]

        outputs = [ItemIO(
            type=i['type'],
            per_minute=i['per_minute'],
            per_cycle=i.get('per_cycle', None),
        ) for i in v['outputs']]

        time = None

        for i in ingredients:
          if i.minutes_per_cycle is not None:
            if time is None:
              time = i.seconds_per_cycle
            elif time != i.seconds_per_cycle:
              warn(f"invalid recipe '{k}' found: inconsistent time values. skipping.")
              raise ValueError

        for i in outputs:
          if i.minutes_per_cycle is not None:
            if time is None:
              time = i.seconds_per_cycle
            elif time != i.seconds_per_cycle:
              warn(f"invalid recipe '{k}' found: inconsistent time values. skipping.")
              raise ValueError

        for i in outputs:
          self.reverse_recipes.setdefault(i.type, []).append(k)

        self.recipes[k] = Recipe(
            allowed_facilities=v.get('allowed_facilities', []),
            ingredients=ingredients,
            name=v.get('name', k),
            outputs=outputs,
            required_power=v.get('required_power', 0.0),
            time=v.get('time', time),
        )
      except KeyError as e:
        warn(f"invalid recipe '{k}' found: {e}")
      except ValueError:
        pass

  def validate(self):
    for k, v in self.recipes.copy().items():
      if v.time is None:
        "warn(f'recipe {k} cannot be infering time and items per cycle. some features may not work.')"

      for f in v.allowed_facilities:
        if f not in self.facilities:
          warn(f"invalid recipe '{k}' found: unknown facility '{f}'. ignoring.")
          self.recipes[k] = Recipe(
              allowed_facilities=[f for f in v.allowed_facilities if f != f],
              ingredients=v.ingredients,
              name=v.name,
              outputs=v.outputs,
              required_power=v.required_power,
              time=v.time,
          )

      for i in v.ingredients:
        if i.type not in self.items:
          warn(f"invalid recipe '{k}' found: unknown item '{i.type}'. Please make sure.")

      for o in v.outputs:
        if o.type not in self.items:
          warn(f"invalid recipe '{k}' found: unknown item '{o.type}'. Please make sure.")
