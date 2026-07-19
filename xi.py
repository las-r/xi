import mcschematic
import sys

# opcode map
OPCODES = {
    "ldi": "000",
    "skp": "001",
    "jmp": "010",
    "hlt": "011",
    "add": "100",
    "sub": "101",
    "nor": "110",
    "shr": "111",
}

def regtobin(reg):
    # 'r3' -> '011', '__' -> '000'
    if reg == "__":
        return "000"
    if reg.startswith("r"):
        val = int(reg[1:])
        return f"{val:03b}"
    raise ValueError(f"Invalid register format: {reg}")

def immtobin(imm, labels=None):
    # int or label name -> 6 bit binary
    if labels and imm in labels:
        val = labels[imm]
    else:
        val = int(imm)

    if val < 0 or val > 63:
        raise ValueError(f"Immediate value {val} out of 6-bit bounds (0-63)")
    return f"{val:06b}"

def assemble(asm):
    labels = {}
    lines = []
    count = 0

    # pass 1: labels
    for linenum, line in enumerate(asm.strip().splitlines(), 1):
        line = line.strip().split(";")[0].strip()  # strip comments
        if not line:
            continue

        if ":" in line:
            label, rest = line.split(":", 1)
            label = label.strip()

            if " " in label:
                raise ValueError(f"Line {linenum}: Invalid label syntax '{label}'")

            labels[label] = count
            line = rest.strip()

            if not line:  # label on its own line
                continue

        lines.append((linenum, line))
        count += 1

    # pass 2: machine code
    bins = []

    for linenum, line in lines:
        tok = line.split()
        op = tok[0].lower()

        if op not in OPCODES:
            raise ValueError(f"Line {linenum}: Unknown opcode '{op}'")

        opc = OPCODES[op]

        try:
            if op == "ldi":
                rx = regtobin(tok[1])
                ii = immtobin(tok[2], labels)
                mc = opc + rx + ii

            elif op == "skp":
                if len(tok) == 2:
                    mc = opc + "000" + "000" + regtobin(tok[1])
                else:
                    mc = opc + regtobin(tok[1]) + regtobin(tok[2]) + regtobin(tok[3])

            elif op == "jmp":
                if len(tok) == 3:
                    mc = opc + "000" + regtobin(tok[1]) + regtobin(tok[2])
                else:
                    mc = opc + regtobin(tok[1]) + regtobin(tok[2]) + regtobin(tok[3])

            elif op == "hlt":
                mc = opc + "000" + "000" + "000"

            elif op in ["add", "sub", "nor"]:
                rx = regtobin(tok[1])
                ry = regtobin(tok[2])
                rz = regtobin(tok[3])
                mc = opc + rx + ry + rz

            elif op == "shr":
                rx = regtobin(tok[1])
                ry = regtobin(tok[2])
                rz = regtobin(tok[3]) if len(tok) > 3 else "000"
                mc = opc + rx + ry + rz

            bins.append(mc)

        except IndexError:
            raise ValueError(f"Line {linenum}: Missing arguments for instruction '{line}'")

    return "\n".join(bins)

def buildschem(compl, outdir, outname):
    prog = mcschematic.MCSchematic()

    x, y, z = -7, 0, -2
    for l in compl:
        for c in l:
            if c == "1":
                if x in [-7, 9]: fc = "west"
                elif x in [-9, 7]: fc = "east"
                prog.setBlock((x, y, z), f"minecraft:redstone_wall_torch[facing={fc}]")
            y -= 2
        y = 0
        z -= 2
        if z < -32:
            z = -2
            if x == -7: x = 9
            elif x == 9: x = -9
            elif x == -9: x = 7

    prog.save(outdir, outname, mcschematic.Version.JE_1_21_5)

# execution
if len(sys.argv) < 2:
    print("Usage: python xi.py <source.asm> [outfile.txt] [schemdir] [schemname]")
    sys.exit(1)

asmf = sys.argv[1]
outf = sys.argv[2] if len(sys.argv) > 2 else "program.txt"

with open(asmf) as f:
    asm = f.read()

outbin = assemble(asm)

with open(outf, "w") as f:
    f.write(outbin + "\n")

print("Compilation successful! Saved to " + outf)
print("Output preview:\n" + outbin)

if len(sys.argv) > 3:
    schemdir = sys.argv[3]
    schemname = sys.argv[4] if len(sys.argv) > 4 else "prog"
    buildschem(outbin.splitlines(), schemdir, schemname)
    print("Schematic saved to " + schemdir + "/" + schemname)