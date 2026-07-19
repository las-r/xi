# Xi
A hyper-minimal 6-bit Minecraft CPU.

## Used Terms
Hexad: 6 bits of data
Triad: 3 bits of data

## Specifications
 - **Clock:** Pulse every 192 ticks (~0.052 hz)
 - **Register File:** 8 hexads, 1 per register (r0-r7, r0 is tied to 0, r5-r7 are sent to display)
 - **Instruction Memory:** 64 instructions worth (128 hexads)
 - **Display:** 6x3
 - **Program Counter:** 1 hexad

## Instructions
### Structure
`o x (y z / ii)` (Each letter corresponds to one triad, `ii` is the last two triads used for immediate loading.)

### Set
| Opcode | Assembly | Description |
| --- | --- | --- |
| 000 | ldi rx ii | rx = ii |
| 001 | skp __ __ rz | pc += 1 if rz != 0 |
| 010 | jmp __ ry rz | pc = ry if rz == 0 |
| 011 | hlt __ __ __ | stop clock |
| 100 | add rx ry rz | rx = ry + rz |
| 101 | sub rx ry rz | rx = ry - rz |
| 110 | nor rx ry rz | rx = ~(ry \| rz) |
| 111 | shr rx ry __ | rx = ry >> 1 |

## Example Program (Fibonacci Sequence)
```asm
ldi r3 3
ldi r1 0
ldi r2 1
add r5 r1 r2
add r1 r2 r0
add r2 r5 r0
jmp r3 r0
```