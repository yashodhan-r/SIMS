"""Falling Sand Simulation — assignment template.

Your task: implement the physics inside ``SandSim.update()`` so that
sand and water behave like they do in real life.

  Sand  -> falls straight down; if blocked, slides diagonally downhill.
  Water -> falls like sand, but when it *can't* fall it spreads sideways.

Only SAND and WATER are required. Fire, smoke, walls, wood, etc. are a
bonus — add a new entry to :class:`Material`, a colour, and a rule.

Run it:  uv run python assignment/temp.py
"""

from __future__ import annotations

from enum import IntEnum

import numpy as np
import pygame


class Material(IntEnum):
    """Every cell in the grid holds one of these values.

    IntEnum means each name is also a normal integer, so a grid can be a
    plain NumPy array of numbers. EMPTY must stay 0 so that a fresh grid
    (which NumPy fills with zeros) starts out as empty space.
    """

    EMPTY = 0
    SAND = 1
    WATER = 2

    # BONUS: add more materials here, e.g.
    # WALL = 3   (immovable — never update it)
    # FIRE = 4   (lives a few ticks, then becomes EMPTY)
    # SMOKE = 5  (rises instead of falling, then fades)


# The colour (R, G, B) drawn for each material.
PALETTE = {
    Material.EMPTY: (0, 0, 0),
    Material.SAND: (194, 178, 128),
    Material.WATER: (52, 120, 235),
}
# Turned into a NumPy array so that looking up a cell's colour is a single
# fast indexing operation: COLORS[grid] gives the RGB value of every cell.
_COLORS = np.array([PALETTE[m] for m in Material], dtype=np.uint8)

# One shared random generator for the whole program. Everything that needs
# a coin-flip (diagonal direction, which side to move) pulls from this.
_rng = np.random.default_rng()


class SandSim:
    """Holds the grid and does the physics + rendering.

    The grid is ``self._types``, a 2D NumPy array of shape (HEIGHT, WIDTH)
    where grid[y, x] is the material at row ``y`` (0 = top) and column
    ``x`` (0 = left).
    """

    def __init__(self, width: int, height: int, cell_size: int = 4, fps: int = 60) -> None:
        self.cell_size = cell_size
        self.fps = fps
        self.brush = Material.SAND
        self.brush_radius = 2
        self.resize_cells(width, height)

    # ------------------------------------------------------------------ #
    # Grid lifecycle
    # ------------------------------------------------------------------ #
    def resize_cells(self, width: int, height: int) -> None:
        """Replace the grid with a fresh empty one of the given size."""
        self.width = int(width)
        self.height = int(height)
        # NumPy fills with zeros = Material.EMPTY. Good.
        self._types = np.zeros((self.height, self.width), dtype=np.uint8)

    def clear(self) -> None:
        """Reset every cell to empty space."""
        self._types[:] = 0

    # ------------------------------------------------------------------ #
    # Painting (mouse input)
    # ------------------------------------------------------------------ #
    def paint_at(self, x: int, y: int) -> None:
        """Place the current brush material in a disc of cells at (x, y).

        ``x``/``y`` are in *grid* coordinates (screen pixels / cell_size).
        """
        r = self.brush_radius
        x0, x1 = max(0, x - r), min(self.width, x + r + 1)
        y0, y1 = max(0, y - r), min(self.height, y + r + 1)
        if x1 <= x0 or y1 <= y0:
            return
        # mgrid gives two grids of y- and x-coordinates over the block;
        # the `disc` mask keeps only cells within a circle of radius r.
        yy, xx = np.mgrid[y0:y1, x0:x1]
        disc = ((xx - x) ** 2 + (yy - y) ** 2) <= r * r
        xs, ys = xx[disc], yy[disc]
        self._types[ys, xs] = int(self.brush)

    # ------------------------------------------------------------------ #
    # Physics
    # ------------------------------------------------------------------ #
    def update(self) -> None:
        """Advance the simulation by one tick. This is YOUR job.

        Rules to implement:

        * Process rows from the BOTTOM up (y = height-1 .. 0). If you go top
          down, a grain falls several cells per tick and flickers.
        * Process columns left-to-right but in a different random order each
          tick, so falling looks symmetrical instead of leaning one way.
        * SAND:
            1. if the cell directly below is EMPTY   -> move straight down
            2. else pick a random side; if the cell down-left or down-right
               is EMPTY -> move diagonally there
            3. else stay put (it rests)
        * WATER: the same as sand, PLUS:
            4. if it couldn't fall at all, move into a random EMPTY
               left/right neighbour — this is what makes water pool flat.

        Hint: if you write straight into the grid you'll re-process cells
        that already moved. Copy the grid before the loop, read from the
        copy, and write the result into the live grid (or vice versa).
        """
        raise NotImplementedError("implement the physics, then delete this line")

    # ------------------------------------------------------------------ #
    # Rendering (boilerplate — nothing to do here)
    # ------------------------------------------------------------------ #
    def surface(self) -> pygame.Surface:
        """Snapshot the grid as a pygame.Surface, scaled up by cell_size.

        _COLORS[grid] turns the cell-material grid into a grid of RGB
        pixels in one shot. pygame expects the axes as (WIDTH, HEIGHT),
        numpy stores them as (HEIGHT, WIDTH), so transpose swaps them back.
        """
        rgb = _COLORS[self._types]
        surf = pygame.surfarray.make_surface(
            np.ascontiguousarray(np.transpose(rgb, (1, 0, 2)))
        )
        if self.cell_size > 1:
            surf = pygame.transform.scale(
                surf, (self.width * self.cell_size, self.height * self.cell_size)
            )
        return surf


def main() -> None:
    """Setup + event loop. Boilerplate — nothing to do here."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Falling Sand — 1 sand, 2 water, 0 erase, [ ] brush, C clear")
    clock = pygame.time.Clock()

    sim = SandSim(800 // 4, 600 // 4)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_1:
                    sim.brush = Material.SAND
                elif k == pygame.K_2:
                    sim.brush = Material.WATER
                elif k in (pygame.K_0, pygame.K_e):
                    sim.brush = Material.EMPTY
                elif k == pygame.K_LEFTBRACKET:
                    sim.brush_radius = max(1, sim.brush_radius - 1)
                elif k == pygame.K_RIGHTBRACKET:
                    sim.brush_radius = min(40, sim.brush_radius + 1)
                elif k == pygame.K_c:
                    sim.clear()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                sim.resize_cells(event.size[0] // sim.cell_size, event.size[1] // sim.cell_size)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            sim.paint_at(mx // sim.cell_size, my // sim.cell_size)

        sim.update()
        screen.blit(sim.surface(), (0, 0))

        pygame.display.flip()
        clock.tick(sim.fps)

    pygame.quit()


if __name__ == "__main__":
    main()