# TowerDefence
Some random First person tower defence game

## Installation & Start up
The dependencies are:
- `sortedcontainers`
- `Panda3d@1.10.8`
which can be installed through `pip`.
You can also install everything using `pipenv install`
if you have `pipenv` installed in your system.

Execute `./src/main.py` or `pipenv run ./src/main.py` for start up.
Note: It takes about 1 minute for the game to start up.
The game might be laggy due the graphics card in the system.
If so, you might want to set `infinite_generation` to `False` in `src/config.py`.


## Game tutorial
### Controls
- `w`: moving forward
- `a`: moving left
- `s`: moving backward
- `d`: moving right
- `q`: loop through the buildable towers. (Left click on empty tile to place.)

### Objective
To defeat the incoming monsters from your precious cake for as long as possible.

### Towers
There are currently only two types of towers.
- ShootTower: A tower that shoots cherries. Costs 40 cherries
- WallTower: A tower that merely blocks of cherries. Costs 30 cherries.

### Monsters
There are currently only two types of monsters.
- Kikiboss: A weak monster that comes in large quantities.
- Dabi: A slow but tough and strong monster.
