"""Generate a two-piece enclosure and STEP assembly for the supplied PCB STEP."""

from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
BOARD_STEP = ROOT / "docs/3d/ESP32-C6-CAN.step"
HOUSING_STEP = ROOT / "docs/3d/ESP32-C6-CAN-enclosure.step"
ASSEMBLY_STEP = ROOT / "docs/3d/ESP32-C6-CAN-enclosed-assembly.step"

BOARD_CENTER_X = 145.9625
BOARD_CENTER_Y = -75.5
BOARD_H1 = (-15.3625, -8.6)

OUTER_X = 48.0
OUTER_Y = 33.0
INNER_X = 42.8
INNER_Y = 28.0
FLOOR_Z = -4.0
CAVITY_FLOOR_Z = -2.55
BASE_TOP_Z = 7.3
LID_THICKNESS = 1.7

LID_SCREWS = ((-22.2, -14.7), (-22.2, 14.7), (22.2, -14.7), (22.2, 14.7))
BOARD_SUPPORTS = ((-18.0, -6.0), (-18.0, 6.0))


def box_at(width: float, depth: float, z0: float, z1: float, x: float, y: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(width, depth, z1 - z0, centered=(True, True, False))
        .translate((x, y, z0))
        .val()
    )


def cylinder_at(radius: float, z0: float, z1: float, x: float, y: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(z1 - z0)
        .translate((x, y, z0))
        .val()
    )


def make_base() -> cq.Shape:
    outer = (
        cq.Workplane("XY")
        .box(OUTER_X, OUTER_Y, BASE_TOP_Z - FLOOR_Z, centered=(True, True, False))
        .translate((0, 0, FLOOR_Z))
        .edges("|Z")
        .fillet(1.2)
        .val()
    )
    cavity = box_at(INNER_X, INNER_Y, CAVITY_FLOOR_Z, BASE_TOP_Z + 0.2, 0, 0)
    base = outer.cut(cavity)

    for x, y in LID_SCREWS:
        base = base.fuse(cylinder_at(1.6, CAVITY_FLOOR_Z, BASE_TOP_Z, x, y))

    for x, y in BOARD_SUPPORTS:
        base = base.fuse(cylinder_at(1.6, CAVITY_FLOOR_Z, -0.05, x, y))

    base = base.fuse(cylinder_at(2.1, CAVITY_FLOOR_Z, -0.05, *BOARD_H1))

    # Connector windows follow the imported connector envelopes with modest clearance.
    port_cutters = (
        box_at(4.2, 10.6, 0.2, 5.4, -22.6, 0.0),  # USB-C
        box_at(10.0, 4.2, 1.1, 6.3, -6.8625, -14.8),  # CAN J3
        box_at(10.0, 4.2, 1.1, 6.3, 2.9375, -14.8),  # UART J4
        box_at(10.0, 4.2, 1.1, 6.3, 0.3375, 14.8),  # I2C J5
        box_at(4.2, 17.2, -2.1, 6.3, 22.6, 0.0),  # MicroSD and SPI J6 edge
    )
    for cutter in port_cutters:
        base = base.cut(cutter)

    # Blind pilot holes accept small self-tapping lid screws; screw hardware is not modeled.
    for x, y in LID_SCREWS:
        base = base.cut(cylinder_at(0.8, CAVITY_FLOOR_Z + 0.15, BASE_TOP_Z + 0.1, x, y))

    base = base.cut(cylinder_at(0.85, CAVITY_FLOOR_Z - 0.05, 0.0, *BOARD_H1))
    return base.clean()


def make_lid() -> cq.Shape:
    lid = box_at(OUTER_X, OUTER_Y, BASE_TOP_Z, BASE_TOP_Z + LID_THICKNESS, 0, 0)
    for x, y in BOARD_SUPPORTS:
        keeper = cylinder_at(1.0, 1.7, BASE_TOP_Z, x, y)
        lid = lid.fuse(keeper)

    for x, y in LID_SCREWS:
        lid = lid.cut(cylinder_at(1.1, BASE_TOP_Z - 0.1, BASE_TOP_Z + LID_THICKNESS + 0.1, x, y))

    # Cable pass-through is aligned to the board's AE2 U.FL connector.
    antenna_xy = (162.0 - BOARD_CENTER_X, -66.5 - BOARD_CENTER_Y)
    lid = lid.cut(cylinder_at(2.0, BASE_TOP_Z - 0.1, BASE_TOP_Z + LID_THICKNESS + 0.1, *antenna_xy))
    return lid.clean()


def import_board() -> cq.Shape:
    board = cq.importers.importStep(str(BOARD_STEP)).val()
    return board.translate(cq.Vector(-BOARD_CENTER_X, -BOARD_CENTER_Y, 0))


def save_assembly(path: Path, parts: tuple[tuple[str, cq.Shape], ...]) -> None:
    assembly = cq.Assembly(name="ESP32-C6 CAN Gateway Enclosure")
    colors = {
        "base": cq.Color(0.22, 0.25, 0.27),
        "lid": cq.Color(0.32, 0.37, 0.38),
        "pcb": cq.Color(0.12, 0.32, 0.20),
    }
    for name, shape in parts:
        assembly.add(shape, name=name, color=colors[name])
    assembly.save(str(path), exportType="STEP")


def main() -> None:
    if not BOARD_STEP.is_file():
        raise FileNotFoundError(f"Source board STEP not found: {BOARD_STEP}")

    board = import_board()
    base = make_base()
    lid = make_lid()

    base_overlap = base.intersect(board).Volume()
    lid_overlap = lid.intersect(board).Volume()
    print(f"Board envelope: {board.BoundingBox()}")
    print(f"Base / board intersect volume: {base_overlap:.6f} mm^3")
    print(f"Lid / board intersect volume: {lid_overlap:.6f} mm^3")
    if base_overlap > 0.01 or lid_overlap > 0.01:
        raise ValueError("Enclosure intersects the supplied PCB assembly; STEP files were not exported")

    save_assembly(HOUSING_STEP, (("base", base), ("lid", lid)))
    save_assembly(ASSEMBLY_STEP, (("base", base), ("pcb", board), ("lid", lid)))
    print(f"Housing STEP: {HOUSING_STEP}")
    print(f"Board-in-housing STEP: {ASSEMBLY_STEP}")


if __name__ == "__main__":
    main()