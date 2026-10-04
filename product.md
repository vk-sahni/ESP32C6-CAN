# Product Brief: ESP32-C6 CAN Telemetry Gateway

## Product Definition

The ESP32-C6 CAN Telemetry Gateway is a compact embedded hardware design intended to interface an ArduPilot-class UAV flight controller's CAN bus with an ESP32-C6FH4. Its role is an auxiliary edge telemetry device. It is not a flight controller and must not be represented as participating in stabilization, navigation, or vehicle safety functions.

The hardware provides a CAN transceiver and protection, MCU, Wi-Fi-capable radio path, MicroSD socket, USB-C USB 2.0 interface, and auxiliary headers. The repository contains the KiCad design, custom library assets, generated board imagery, and STEP export. It does not contain operational firmware or cloud software.

## Intended System

```text
ArduPilot flight controller
        | CAN / DroneCAN
        v
ESP32-C6 CAN gateway hardware
        | Wi-Fi radio path (firmware not included)
        v
Internet and telemetry service (not included)
```

The board also has a MicroSD socket intended as a possible local storage endpoint. Card initialization and logging firmware are not present. Cloud telemetry, data decoding, store-and-forward behavior, APIs, databases, and dashboards are future work, not current product capabilities.

## Hardware Blocks

| Block | Reference | Verified design detail |
|---|---|---|
| MCU | U1 | ESP32-C6FH4 package/footprint, integrated Wi-Fi radio |
| RF connection | AE2 | U.FL connector footprint and RF matching path |
| CAN transceiver | U3 | TCAN332, powered from +3V3 |
| CAN-line protection | D3 | NUP2105L connected to CANH, CANL, and GND |
| CAN resistor | R16 | 120 ohm across CANH and CANL |
| CAN connector | J3 | 4-position JST GH footprint: VBUS, CANH, CANL, GND |
| Regulator | U2 | TC2014-3.3VxCTTR; input is connected to VBUS |
| Removable storage | J2 | MicroSD socket; DAT1 and DAT2 are marked no-connect |
| USB | J1 | USB-C receptacle with USB 2.0 D+ / D- and VBUS |
| USB VBUS protection | D2 | SZESD9B5.0ST5G protection diode |
| Auxiliary headers | J4-J6 | UART telemetry, I2C, and External SPI labels in schematic |

Header labels document intended electrical interfaces. They do not prove support in firmware or identify a tested pin configuration beyond the connected schematic nets.

## Interfaces and Power

J3 pin 1 (VBUS) is on the same VBUS net as the USB-C VBUS pins and U2 regulator input. This is a meaningful system integration constraint: review the source/sink arrangement before powering through more than one connector. Do not assume the connector's VBUS pin is isolated.

The CAN nets are named `CANH` and `CANL` in the schematic. R16 is a 120 ohm resistor placed across the pair on the board. Whether this termination is suitable depends on the gateway's location and termination plan on the complete bus.

The board's power circuit includes a TC2014 3.3 V regulator and a +3V3 net. No input-current, output-current, thermal, or power-budget test results are included.

The ESP32-C6 antenna net passes through matching components to AE2, a U.FL connector footprint. An antenna part, RF range, regulatory approval, and conducted/radiated performance are not established by the repository.

## Technical Envelope

| Attribute | Design value / status |
|---|---|
| MCU | ESP32-C6FH4 |
| CAN transceiver | TCAN332; symbol metadata indicates 1 Mbps capability |
| Project CAN data rate | Not specified or validated |
| CAN protection | NUP2105L |
| CAN termination component | 120 ohm R16 across CANH/CANL |
| Removable storage | MicroSD socket; DAT1/DAT2 no-connect |
| USB | USB-C receptacle, USB 2.0 D+/D- |
| Logic rail | +3V3 |
| RF connector | U.FL footprint/model at AE2 |
| Board outline | 40 x 25 mm as dimensioned in PCB |
| Copper layers | Four-layer KiCad stackup |

The outline and stackup are design-file properties, not manufacturing tolerances or production specifications. The 1 Mbps note is a transceiver-symbol capability, not a tested project bus rate.

## Product Status

| Capability | Status |
|---|---|
| KiCad schematic and routed PCB | Present in repository |
| ESP32-C6, CAN transceiver, protection, and connectors | Present in schematic/PCB design |
| Wi-Fi telemetry firmware | Not included |
| CAN/DroneCAN driver and message decoding | Not included |
| MicroSD flight logging | Not included |
| Cloud transport, API, database, dashboard | Not included |
| Electrical, RF, environmental, or flight validation | Not reported |

## Safety and Reliability Notes

The documented read-only KiCad DRC run reports 154 counted violations, including via geometry, clearances, holes, and silkscreen/edge findings, as well as two schematic-parity issues. It also reports zero unconnected pads. The DRC report separately lists a missing H2 footprint and local-override warnings for the J1 library-footprint mismatch and J6 symbol/footprint value mismatch. Review and resolve these before fabrication; this documentation work did not modify the circuit or PCB.

This hardware has not been presented as flight-qualified or safety-rated. Validate power sequencing, CAN termination, connector wiring, thermal limits, RF performance, and behavior under faults before use in a UAV or other safety-relevant system.

## Visual and CAD Assets

- [Product hero render](docs/images/hero-product.png)
- [PCB front 3D render](docs/images/pcb-3d-front.png)
- [PCB isometric 3D render](docs/images/pcb-3d-angle.png)
- [PCB reverse-side 3D render](docs/images/pcb-3d-back.png)
- [Board STEP assembly](docs/3d/ESP32-C6-CAN.step)
- [Hardware block diagram](docs/diagrams/hardware-block-diagram.svg)
- [System architecture](docs/diagrams/system-architecture.svg)
- [CAN interface](docs/diagrams/can-interface.svg)
- [Telemetry data flow](docs/diagrams/telemetry-data-flow.svg)
