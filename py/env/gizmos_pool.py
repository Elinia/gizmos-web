from random import shuffle
from typing import Literal, TypedDict

from .common import BuildMethod, Energy, GizmoLevel
from .Gizmo import Gizmo, BuildGizmo, ConverterGizmo, FileGizmo, PickGizmo, UpgradeGizmo


id: int = -1


def file_draw_level0():
    global id
    id += 1
    return FileGizmo(
        id=id,
        level=0,
        energy_type="any",
        energy_cost=0,
        value=0,
        effect={
            "type": "free_draw",
            "num": 1,
        },
    )


def init_level0() -> list[Gizmo]:
    return [
        file_draw_level0(),
        file_draw_level0(),
        file_draw_level0(),
        file_draw_level0(),
    ]


LEVEL1_COMMON: dict[Literal["level", "energy_cost", "value"], int] = {
    "level": 1,
    "energy_cost": 1,
    "value": 1,
}

BUILD_COMMON: dict[Literal["level", "method"], Literal["any"]] = {
    "level": "any",
    "method": "any",
}


def build_point_level1(energy_type: Energy, build_energy: Energy):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": [build_energy],
        },
        effect={
            "type": "add_point_token",
            "num": 1,
        },
    )


def build_pick_level1(energy_type: Energy, build_energy: Energy):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": [build_energy],
        },
        effect={
            "type": "free_pick",
            "num": 1,
        },
    )


def upgrade_ef_level1(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        max_energy_num=1,
        max_file_num=1,
    )


def upgrade_er_level1(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        max_energy_num=1,
        research_num=1,
    )


def file_pick_level1(energy_type: Energy):
    global id
    id += 1
    return FileGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        effect={
            "type": "free_pick",
            "num": 1,
        },
    )


def pick_draw_level1(energy_type: Energy, pick_energy: Energy):
    global id
    id += 1
    return PickGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        when_pick=[pick_energy],
        effect={
            "type": "free_draw",
            "num": 1,
        },
    )


def converter_level1(energy_type: Energy, from_energy: Energy):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **LEVEL1_COMMON,
        energy_type=energy_type,
        formulae=[
            {
                "from": {
                    "energy": from_energy,
                    "num": 1,
                },
                "to": {
                    "energy": "any",
                    "num": 1,
                },
            },
        ],
    )


def init_level1() -> list[Gizmo]:
    return [
        build_point_level1("yellow", "blue"),
        build_point_level1("blue", "black"),
        build_point_level1("black", "red"),
        build_point_level1("red", "yellow"),
        build_pick_level1("red", "black"),
        build_pick_level1("black", "blue"),
        build_pick_level1("blue", "yellow"),
        build_pick_level1("yellow", "red"),
        upgrade_ef_level1("red"),
        upgrade_ef_level1("black"),
        upgrade_ef_level1("blue"),
        upgrade_ef_level1("yellow"),
        upgrade_er_level1("red"),
        upgrade_er_level1("black"),
        upgrade_er_level1("blue"),
        upgrade_er_level1("yellow"),
        file_pick_level1("red"),
        file_pick_level1("black"),
        file_pick_level1("blue"),
        file_pick_level1("yellow"),
        pick_draw_level1("yellow", "red"),
        pick_draw_level1("red", "blue"),
        pick_draw_level1("blue", "black"),
        pick_draw_level1("black", "yellow"),
        pick_draw_level1("blue", "red"),
        pick_draw_level1("red", "yellow"),
        pick_draw_level1("yellow", "black"),
        pick_draw_level1("black", "blue"),
        converter_level1("red", "blue"),
        converter_level1("red", "black"),
        converter_level1("yellow", "blue"),
        converter_level1("yellow", "black"),
        converter_level1("blue", "red"),
        converter_level1("blue", "yellow"),
        converter_level1("black", "red"),
        converter_level1("black", "yellow"),
    ]


def level2_common(cost: int):
    return {
        "level": 2,
        "energy_cost": cost,
        "value": cost,
    }


def converter_double_level2(energy_type: Energy, from_energy: Energy):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **level2_common(3),
        energy_type=energy_type,
        formulae=[
            {
                "from": {
                    "energy": from_energy,
                    "num": 1,
                },
                "to": {
                    "energy": from_energy,
                    "num": 2,
                },
            },
        ],
    )


def converter_any_level2(energy_type: Energy, from_energy: Energy):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **level2_common(2),
        energy_type=energy_type,
        formulae=[
            {
                "from": {
                    "energy": from_energy,
                    "num": 1,
                },
                "to": {
                    "energy": "any",
                    "num": 1,
                },
            },
            {
                "from": {
                    "energy": from_energy,
                    "num": 1,
                },
                "to": {
                    "energy": "any",
                    "num": 1,
                },
            },
        ],
    )


def build_pick_level2(energy_type: Energy, build_energy: list[Energy]):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level2_common(2),
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": build_energy,
        },
        effect={
            "type": "free_pick",
            "num": 1,
        },
    )


def build_point_level2(energy_type: Energy, build_energy: list[Energy]):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level2_common(3),
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": build_energy,
        },
        effect={
            "type": "add_point_token",
            "num": 1,
        },
    )


def build_from_file_pick_level2(energy_type: Energy):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level2_common(3),
        energy_type=energy_type,
        when_build=dict(
            level="any",
            method=[BuildMethod.FROM_FILED],
            energy="any",
        ),
        effect=dict(
            type="free_pick",
            num=2,
        ),
    )


def pick_draw_level2(energy_type: Energy, pick_energy: list[Energy]):
    global id
    id += 1
    return PickGizmo(
        id=id,
        **level2_common(2),
        energy_type=energy_type,
        when_pick=pick_energy,
        effect=dict(
            type="free_draw",
            num=1,
        ),
    )


def upgrade_level2(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **level2_common(3),
        energy_type=energy_type,
        max_energy_num=2,
        max_file_num=1,
        research_num=2,
    )


def init_level2() -> list[Gizmo]:
    return [
        converter_double_level2("red", "black"),
        converter_double_level2("black", "red"),
        converter_double_level2("yellow", "blue"),
        converter_double_level2("blue", "yellow"),
        converter_double_level2("red", "blue"),
        converter_double_level2("blue", "red"),
        converter_double_level2("yellow", "black"),
        converter_double_level2("black", "yellow"),
        converter_any_level2("yellow", "red"),
        converter_any_level2("red", "yellow"),
        converter_any_level2("blue", "black"),
        converter_any_level2("black", "blue"),
        build_pick_level2("blue", ["yellow", "black"]),
        build_pick_level2("blue", ["yellow", "red"]),
        build_pick_level2("yellow", ["black", "red"]),
        build_pick_level2("yellow", ["blue", "black"]),
        build_pick_level2("red", ["blue", "yellow"]),
        build_pick_level2("red", ["blue", "black"]),
        build_pick_level2("black", ["red", "blue"]),
        build_pick_level2("black", ["yellow", "red"]),
        build_point_level2("yellow", ["red", "blue"]),
        build_point_level2("red", ["yellow", "black"]),
        build_point_level2("black", ["blue", "yellow"]),
        build_point_level2("blue", ["black", "red"]),
        build_from_file_pick_level2("black"),
        build_from_file_pick_level2("blue"),
        build_from_file_pick_level2("red"),
        build_from_file_pick_level2("yellow"),
        pick_draw_level2("yellow", ["red", "blue"]),
        pick_draw_level2("red", ["blue", "black"]),
        pick_draw_level2("blue", ["yellow", "black"]),
        pick_draw_level2("black", ["yellow", "red"]),
        upgrade_level2("black"),
        upgrade_level2("blue"),
        upgrade_level2("red"),
        upgrade_level2("yellow"),
    ]


def level3_common(cost: int):
    return dict(
        level=3,
        energy_cost=cost,
        value=cost,
    )


def upgrade_e_level3(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **level3_common(4),
        energy_type=energy_type,
        max_energy_num=4,
    )


def upgrade_forbid_file_level3(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        level=3,
        energy_cost=4,
        value=7,
        energy_type=energy_type,
        max_file_num=-200,
    )


def upgrade_forbid_research_level3(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        level=3,
        energy_cost=4,
        value=8,
        energy_type=energy_type,
        research_num=-200,
    )


def upgrade_token_as_point_level3():
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        level=3,
        energy_type="any",
        energy_cost=7,
        value=0,
        effect=dict(
            type="token_as_point",
        ),
    )


def upgrade_energy_as_point_level3():
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        level=3,
        energy_type="any",
        energy_cost=7,
        value=0,
        effect=dict(
            type="energy_as_point",
        ),
    )


def upgrade_build_from_filed_cost_reduction_level3(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        build_from_filed_cost_reduction=1,
    )


def upgrade_build_from_research_cost_reduction_level3(energy_type: Energy):
    global id
    id += 1
    return UpgradeGizmo(
        id=id,
        **level3_common(6),
        energy_type=energy_type,
        build_from_research_cost_reduction=1,
    )


def file_draw_level3(energy_type: Energy):
    global id
    id += 1
    return FileGizmo(
        id=id,
        **level3_common(4),
        energy_type=energy_type,
        effect=dict(
            type="free_draw",
            num=3,
        ),
    )


def file_point_level3(energy_type: Energy):
    global id
    id += 1
    return FileGizmo(
        id=id,
        **level3_common(4),
        energy_type=energy_type,
        effect=dict(
            type="add_point_token",
            num=1,
        ),
    )


def build_point_level3(
    energy_type: Energy, build_energy: list[Energy] | Literal["any"]
):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": build_energy,
        },
        effect=dict(
            type="add_point_token",
            num=2,
        ),
    )


def build_pick_level3(energy_type: Energy):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(6),
        energy_type=energy_type,
        when_build={
            "level": [2],
            "energy": "any",
            "method": "any",
        },
        effect=dict(
            type="free_pick",
            num=2,
        ),
    )


def build_from_file_point_level3(energy_type: Energy):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        when_build={
            "level": "any",
            "method": [BuildMethod.FROM_FILED],
            "energy": "any",
        },
        effect=dict(
            type="add_point_token",
            num=2,
        ),
    )


def build_file_level3(energy_type: Energy, build_energy: list[Energy] | Literal["any"]):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        when_build={
            **BUILD_COMMON,
            "energy": build_energy,
        },
        effect=dict(
            type="extra_file",
        ),
    )


def build_research_level3(
    energy_type: Energy, build_energy: list[Energy] | Literal["any"]
):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(7),
        energy_type=energy_type,
        when_build=dict(
            **BUILD_COMMON,
            energy=build_energy,
        ),
        effect=dict(
            type="extra_research",
        ),
    )


def build_build_level3(
    energy_type: Energy, build_energy: list[Energy] | Literal["any"]
):
    global id
    id += 1
    return BuildGizmo(
        id=id,
        **level3_common(6),
        energy_type=energy_type,
        when_build=dict(
            **BUILD_COMMON,
            energy=build_energy,
        ),
        effect=dict(
            type="extra_build",
            level=[1],
        ),
    )


def converter_double_level3(energy_type: Energy, from_energy: list[Energy]):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        formulae=list(
            map(
                lambda energy: {
                    "from": {
                        "energy": energy,
                        "num": 1,
                    },
                    "to": {
                        "energy": energy,
                        "num": 2,
                    },
                },
                from_energy,
            ),
        ),
    )


def converter_any_level3(energy_type: Energy):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **level3_common(4),
        energy_type=energy_type,
        formulae=[
            {
                "from": {
                    "energy": "any",
                    "num": 1,
                },
                "to": {
                    "energy": "any",
                    "num": 1,
                },
            },
        ],
    )


def converter_cost_reduction_level3(energy_type: Energy):
    global id
    id += 1
    return ConverterGizmo(
        id=id,
        **level3_common(5),
        energy_type=energy_type,
        prerequisite=dict(
            level=[2],
        ),
        formulae=[
            {
                "from": {
                    "energy": "any",
                    "num": 0,
                },
                "to": {
                    "energy": "any",
                    "num": 1,
                },
            },
        ],
    )


def init_level3() -> list[Gizmo]:
    return [
        upgrade_e_level3("blue"),
        upgrade_e_level3("black"),
        upgrade_forbid_file_level3("red"),
        upgrade_forbid_file_level3("blue"),
        upgrade_forbid_research_level3("yellow"),
        upgrade_forbid_research_level3("black"),
        upgrade_energy_as_point_level3(),
        upgrade_energy_as_point_level3(),
        upgrade_token_as_point_level3(),
        upgrade_token_as_point_level3(),
        upgrade_build_from_filed_cost_reduction_level3("red"),
        upgrade_build_from_filed_cost_reduction_level3("blue"),
        upgrade_build_from_research_cost_reduction_level3("yellow"),
        upgrade_build_from_research_cost_reduction_level3("black"),
        file_draw_level3("yellow"),
        file_draw_level3("blue"),
        file_point_level3("red"),
        file_point_level3("black"),
        build_point_level3("red", ["yellow", "black"]),
        build_point_level3("black", ["red", "blue"]),
        build_pick_level3("red"),
        build_pick_level3("black"),
        build_from_file_point_level3("yellow"),
        build_from_file_point_level3("red"),
        build_file_level3("yellow", ["black", "red"]),
        build_file_level3("black", ["blue", "yellow"]),
        build_research_level3("red", ["blue", "black"]),
        build_research_level3("blue", ["yellow", "red"]),
        build_build_level3("yellow", ["blue", "black"]),
        build_build_level3("blue", ["yellow", "red"]),
        converter_double_level3("blue", ["black", "red"]),
        converter_double_level3("black", ["blue", "yellow"]),
        converter_any_level3("red"),
        converter_any_level3("yellow"),
        converter_cost_reduction_level3("yellow"),
        converter_cost_reduction_level3("blue"),
    ]


class InitGizmos(TypedDict):
    gizmos: list[Gizmo]
    gizmos_pool: dict[GizmoLevel, list[Gizmo]]


l0 = init_level0()
l1 = init_level1()
l2 = init_level2()
l3 = init_level3()
gizmos = [*l0, *l1, *l2, *l3]
for g, i in zip(gizmos, range(len(gizmos))):
    if g.id != i:
        raise Exception("id inconsistent")


def init_gizmos() -> InitGizmos:
    for gizmo in gizmos:
        gizmo.reset()
    l1_s = list(l1)
    l2_s = list(l2)
    l3_s = list(l3)
    for g in l1_s:
        g.where = "pool"
    for g in l2_s:
        g.where = "pool"
    for g in l3_s:
        g.where = "pool"
    shuffle(l1_s)
    shuffle(l2_s)
    shuffle(l3_s)
    return {
        "gizmos": gizmos,
        "gizmos_pool": {
            1: l1_s,
            2: l2_s,
            3: l3_s[:16],
        },
    }
