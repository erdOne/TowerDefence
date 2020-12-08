"""Configurations."""
from utils import Object

map_params = Object(
    unit_size=10,
    height=20,
    cell_size=3,
    wall_width=1,
    field_size=16,
    town_size=2,
    seed=10,
    colors=Object(
        wall=(1, 0.5, 0.5, 1),
        floor=(0.5, 0.5, 1, 1)
    )
)

key_map = Object(
    character=Object(
        forward="w",
        backward="s",
        left="a",
        right="d"
    ),
    utility=Object(
        pause="escape"
    )
)

physics = Object(
    walk_accel=45,
    max_speed=30,
    stop_friction=10,
    friction=10,
    keep_velocity=0.5
)

mouse_params = Object(
    heading_speed=90,
    pitch_speed=90
)

minimap = Object(
    height=100,
    size=300,
    colors=Object(
        player=(0.5, 1, 0.5, 1)
    )
)
