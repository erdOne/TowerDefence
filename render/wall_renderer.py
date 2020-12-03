"""Render a wall."""
from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    Geom,
    GeomVertexWriter,
    GeomTriangles
)
from utils import Object

class WallRenderer:
    """Create a wall Geom object with front left bottom corner at pos."""

    def __init__(self, pos, dims, color, faces):
        """
        Init the class.

        faces is a list of bools of len 4
        representing the existence of
        left(x = 0), right, front(y = 0), back faces respectively
        """
        self.vertex_list = GeomVertexData(
            'vertex_list', GeomVertexFormat.get_v3n3c4(), Geom.UHStatic)
        self.pos = pos
        self.dims = dims
        self.color = color
        self.faces = faces
        self.vertex_list.setNumRows(12)
        self.writers = Object(
            vertex=GeomVertexWriter(self.vertex_list, 'vertex'),
            normal=GeomVertexWriter(self.vertex_list, 'normal'),
            color=GeomVertexWriter(self.vertex_list, 'color')
        )
        self.geom = None

    def add_rectangle(self, orientation, *vertices):
        """Add a rectangle with dir into geom."""
        vertices = [i*3+orientation for i in vertices]
        rectangle = GeomTriangles(Geom.UHStatic)
        rectangle.addVertices(vertices[0], vertices[1], vertices[2])
        rectangle.addVertices(vertices[2], vertices[3], vertices[0])
        rectangle.close_primitive()
        self.geom.addPrimitive(rectangle)

    def write_faces(self):
        """Add the six faces of the wall."""
        # self.add_rectangle(2, 0, 2, 3, 1)  # down
        self.faces[0] and self.add_rectangle(0, 0, 4, 6, 2)  # left
        self.faces[1] and self.add_rectangle(0, 1, 3, 7, 5)  # right
        self.faces[2] and self.add_rectangle(1, 0, 1, 5, 4)  # front
        self.faces[3] and self.add_rectangle(1, 2, 6, 7, 3)  # back
        self.add_rectangle(2, 4, 5, 7, 6)  # top

    def write_vertices(self):
        """Add the eight vertices of the wall."""
        for i in range(8):
            for j in range(3):
                self.writers.vertex.addData3(
                    self.pos[0]+self.dims[0]*(i & 1),
                    self.pos[1]+self.dims[1]*(i >> 1 & 1),
                    self.pos[2]+self.dims[2]*(i >> 2 & 1)
                )
                self.writers.normal.addData3(
                    ((i << 1 & 2)-1)*(j == 0),
                    ((i & 2)-1)*(j == 1),
                    ((i >> 1 & 2)-1)*(j == 2)
                )
                self.writers.color.addData4(*self.color)

    def get_geom(self):
        """Retreive geom object."""
        self.write_vertices()
        self.geom = Geom(self.vertex_list)
        self.write_faces()
        return self.geom
