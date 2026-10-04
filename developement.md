# Development Notes

This document describes the current state and practical workflow for contributors to the ESP32-C6 CAN Telemetry Gateway hardware repository.

## Repository Scope

The repository currently contains KiCad design sources and libraries. It does not contain firmware, a build system for the ESP32-C6, cloud services, or a web dashboard. Firmware and service blocks shown in the diagrams are proposals only.

| Area | Current state |
|---|---|
| Schematic | `ESP32-C6FH4.kicad_sch` and `Connectors.kicad_sch` |
| PCB | `ESP32-C6FH4.kicad_pcb` |
| Project settings | `ESP32-C6FH4.kicad_pro` |
| Custom libraries | `lib/footprints.pretty`, `lib/symbol`, `lib/packages3d` |
| Product documentation | `README.md`, `product.md`, `docs/` |
| Firmware / cloud | Not included |

Open `ESP32-C6FH4.kicad_pro` in KiCad to work with the design. Keep the existing KiCad filenames and project-relative custom library/3D-model paths unless a coordinated migration is needed.

## Change Workflow

1. Review both schematic sheets and the PCB before changing a symbol, footprint, net, or connector.
2. Make electrical changes in the schematic first, then update the PCB and verify schematic/PCB parity.
3. Preserve connector pin order and review the shared power nets, CAN termination, and protection whenever the interface changes.
4. Update product diagrams and documentation if the verified design changes. Keep planned firmware paths visually distinct from present hardware.
5. Run ERC/DRC and inspect the 3D view before proposing fabrication files.
6. Summarize known limitations and validation actually performed; do not infer successful firmware operation from the hardware design.

## Useful KiCad CLI Checks

Run commands from the repository root. These commands read the project; avoid using `--save-board` or any option that writes the PCB unless that change is intentional.

```sh
kicad-cli sch export netlist --format kicadxml \
  --output /tmp/ESP32-C6FH4-netlist.xml ESP32-C6FH4.kicad_sch

kicad-cli pcb drc --output /tmp/ESP32-C6FH4-drc.txt \
  --format report --schematic-parity ESP32-C6FH4.kicad_pcb

kicad-cli pcb render --output /tmp/ESP32-C6FH4-render.png \
  --width 2200 --height 1500 --side top --quality high \
  --preset follow_pcb_editor --use-board-stackup-colors \
  ESP32-C6FH4.kicad_pcb

kicad-cli pcb export step --output /tmp/ESP32-C6FH4.step \
  --include-tracks --include-pads ESP32-C6FH4.kicad_pcb

python docs/3d/design_enclosure.py
```

Review warnings and errors rather than treating a successful command exit as proof that the board is fabrication-ready.

The enclosure script imports `docs/3d/ESP32-C6-CAN.step`, builds a base and lid, checks each solid against the imported board assembly, and writes `ESP32-C6-CAN-enclosure.step` plus `ESP32-C6-CAN-enclosed-assembly.step`. It requires CadQuery 2.8 and its OpenCascade kernel. The geometry guard checks solid intersection only; it does not model print tolerances or verify physical fit.

## Current Validation Record

A read-only KiCad DRC run with schematic parity reported:

- 154 counted violations: 52 via-diameter, 52 annular-width, 38 copper-clearance, 4 hole-clearance, 3 hole-to-hole, 2 silkscreen-edge, 2 copper-edge-clearance, and 1 missing H2 footprint.
- Two schematic-parity issues and zero unconnected pads.
- Separate footprint/local-override warnings for H2, the J6 symbol/footprint value mismatch, and the J1 library-footprint mismatch. These warnings are listed separately from the 154 counted DRC violations.

This report was generated from the current local board and project settings. It is not a sign-off. Resolve and review the findings before release or fabrication; no electrical/PCB edits were part of the documentation task.

## Firmware Roadmap

Firmware tasks below are future work; none are implemented in this repository:

- Select and document the CAN controller/driver and supported ArduPilot / DroneCAN messages.
- Define node identity, frame handling, timeouts, and any protocol-level behavior.
- Plan bounded buffering and explicit behavior when Wi-Fi, storage, or the CAN bus is unavailable.
- Implement and test MicroSD initialization, file format, writes, and recovery after power loss.
- Implement Wi-Fi configuration, transport, security, and reconnect behavior.
- Specify a cloud API/protocol and backend only when a concrete implementation exists.
- Add hardware-in-loop, bench, RF, and flight-test evidence before making performance claims.

Do not call the future telemetry path “store-and-forward” until buffering, durable storage, and replay behavior exist and have been tested.

## Hardware Review Checklist

Before a hardware revision or fabrication release, at minimum:

- Re-run KiCad ERC, DRC, and schematic-parity checks and review every violation.
- Resolve the H2 mounting-hole footprint issue and J6/J1 footprint consistency warnings.
- Verify whether the fixed 120 ohm resistor R16 is correct for the intended bus topology.
- Review J3 pin 1 VBUS sharing with USB-C VBUS and U2 VIN; define power-source behavior and protection.
- Confirm pin numbering and cable polarity for CAN, UART, I2C, SPI, and power.
- Confirm the MicroSD wiring, no-connect pins, card voltage/pull-ups, and intended bus width.
- Check the BOM, footprint assignments, 3D models, board outline, assembly details, and manufacturing constraints.
- Perform bench tests for power, CAN traffic, USB, SD-card access, and RF only after relevant firmware exists.

## Documentation Rules

- The schematic and PCB are the source of truth for hardware labels and connections.
- Keep all block names, nets, and pinouts matched to the KiCad design.
- Mark software or service components as **Planned** unless implementation and tests are present in this repository.
- Do not advertise unmeasured CAN bitrate, current, RF range, temperature, reliability, or flight safety.
- Keep render source images and editable SVG diagrams under `docs/`.
