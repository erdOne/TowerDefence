"""Configurations."""
from utils import Object, color


map_params = Object(
    unit_size=10,
    height=20,
    cell_size=3,
    wall_width=1,
    field_size=15,
    core_size=3,
    center_size=3,
    seed=10,
    colors=Object(
        wall=(1, 0.5, 0.5, 1),
        floor=color("94DEFF"),
        sky=color("FFF9D9")
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

player = Object(
    size=2
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
