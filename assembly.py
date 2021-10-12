
import golly as g
import math
import re

"""
programing instructions:

variable names start by "a" followed by a number. eg a1 a2 a3 a10 are good variable names
a0 is used for storing the current program line, so be carefull, modifiying a0 will jump to the line a0
the instructions are:

(let be n an integer in base 10)

write a1 n
-> write n to the variable a1 (written in 2's complement if signed)

goto n
-> go to the line n (first line is line 0)

move a1 a2
-> a1=a2

jump a1
-> jump the a1 next lines

print a1
-> print a1

disp a1 a2
-> draw a pixel of coordinates a1 a2

erase
-> erase the 2d display

rfb a1 a2
-> a1 = memory[a2] ; write the content of the address stored in a2 to a1; (if a2=N, a1=aN)

wfb a1 a2
-> memory[a2] = a1 ; write a1 to the address stored in a2; (if a2=N, aN=a1)

++ a1 a2
-> a1=a2+1

- a1 a2 a3
-> a1 = a2-a3

+ a1 a2 a3
-> a1 = a2+a3

or a1 a2 a3
-> a1=bitwiseOR(a2,a3)

and a1 a2 a3
-> a1=bitwiseAND(a2,a3)

xor a1 a2 a3
-> a1=bitwiseXOR(a2,a3)

not a1 a2
-> a1=bitwiseNOT(a2)

>> a1 a2
-> a1 = shift_right(a2)

<< a1 a2
-> a1 = shift_left(a2)

rr a1 a2
-> a1 = rotate_right(a2)

rl a1 a2
-> a1 = rotate_left(a2)

=0 a1 a2
-> a1 = 1 if a2==0 else a1=0

!=0 a1 a2
-> a1 = 1 if a2!=0 else a1=0

less a1 a2
-> a1 = 1 if less_significant_bit(a2)==1 else a1=0

most a1 a2
-> a1 = 1 if most_significant_bit(a2)==1 else a1=0

*- a1 a2
-> a1 = -a2
"""

M = 8 #size of the variables. can be 8, 16 or 32

# write your program here
# (this example draws a square in a circle)
program = """
write a7 1
write a1 15
move a3 a1
write a6 1
write a4 0
- a2 a6 a1
+ a5 a1 a3
+ a6 a1 a4
disp a5 a6
disp a6 a5
- a5 a1 a3
disp a5 a6
disp a6 a5
+ a5 a1 a3
- a6 a1 a4
disp a5 a6
disp a6 a5
- a5 a1 a3
disp a5 a6
disp a6 a5
++ a4 a4
<< a5 a4
most a6 a2
and a6 a6 a7
<< a6 a6
<< a6 a6
jump a6
write a6 1
- a3 a3 a6
- a5 a4 a3
<< a5 a5
+ a2 a2 a5
++ a2 a2
- a5 a3 a4
most a5 a5
jump a5
goto 6
write a7 0
goto 1
"""


program = program.rstrip(" \n")
program = program.lstrip(" \n")

addresses = re.findall('a[0-9]+', program)
Ns = [int(a[1:]) for a in addresses]
N = 2**int(math.ceil(math.log(max(Ns)+1,2)))
N = max(4,N)

P = len(program.split("\n"))
P = 2**int(math.ceil(math.log(P+1,2)))
P = max(16,P)

instructions = [" ","++", "-", "+", "or", "and", "xor", "not",">>","<<",
                    "rr","rl","=0","!=0","less","most","write","move","rfb","wfb","disp","erase","print","*-"]
alu1 = ["++", "not",">>","<<","rr","rl","=0","!=0","less","most","move","*-"]
alu2 = ["-", "+", "or", "and", "xor"]



def twos_complement(v):
	v = bin(-v)[2:].zfill(M)
	v = "".join(["0" if c=="1" else "1" for c in v])
	v = int(v,2)+1
	v = bin(v)[2:].zfill(M)
	return v

def preprocess(program):
    program = program.split("\n")
    return map(preprocess_line,program)


def preprocess_line(line):
    line = line.split()
    instruction = line[0]
    if not instruction in instructions+["goto", "jump"]:
        raise ValueError('Unknown instruction. Add is +; subtract is -; increment is ++; multiply by -1 is *-')
    aw = 'a0'
    ar1 = 'a0'
    ar2 = 'a0'
    data = 0
    i = line[0]
    if instruction in alu1:
        aw = line[1]
        ar1 = line[2]
    elif instruction in alu2:
        aw = line[1]
        ar1 = line[2]
        ar2 = line[3]
    if instruction == "-":
        aw = line[1]
        ar1 = line[3]
        ar2 = line[2]
    if instruction == "write":
        # write address value
        aw = line[1]
        data = line[2]
    if instruction == "rfb":
        # rfb target_address index_address
        aw = line[1]
        ar2 = line[2]
    if instruction == 'wfb':
        # wfb source_address index_address
        ar1 = line[1]
        ar2 = line[2]
    if instruction == 'disp':
        # disp address1 address2
        ar1 = line[1]
        ar2 = line[2]
    if instruction == 'print':
        # print address1
        ar1 = line[1]
    if instruction == 'goto':
        # goto value_to_go_to
        i = "write"
        data = line[1]
    if instruction == 'jump':
        # jump address_to_add_to_pc
        i = "+"
        ar1 = line[1]
    return " ".join([i,aw,ar1,ar2,str(data)])

def assemble(lines):
    return list(map(assemble_line, lines))

def assemble_line(line):
    i = [" ","++", "-", "+", "or", "and", "xor", "not",">>","<<",
                "rr","rl","=0","!=0","less","most","write","move","rfb","wfb","disp","erase","print","*-"]
    line = line.split()
    instruction = i.index(line[0])
    aw = int(line[1][1:])
    ar1 = int(line[2][1:])
    ar2 = int(line[3][1:])
    value = int(line[4])
    return bin_from_id(instruction, aw, ar1, ar2, value)

def bin_from_id(instruction, aw, ar1, ar2, value):
    instruction = bin(instruction)[2:].zfill(5)
    aw = bin(aw)[2:].zfill(Nd)
    ar1 = bin(ar1)[2:].zfill(Nd)
    ar2 = bin(ar2)[2:].zfill(Nd)
    if value >= 0:
        value = bin(value)[2:].zfill(M)[::-1]
    else:
        value = twos_complement(value)
    return instruction+aw+ar1+ar2+value

def write_program(x,y,data,w=200):
    g.addlayer()
    g.open("bit2.mc")
    g.select([-w, -w, w*2, w*2])
    g.copy()
    g.dellayer()
    di = 4*30
    dj = Pd*2*30
    dj2 = 2*30
    for il, line in enumerate(data):
        d1 = 0
        k = 0
        for i in range(5):
            if line[k]=="1":
                g.paste(x+d1+di*i+il*dj, y-d1-di*i+il*dj, "or")
            k+=1
        d2 = 30*30*4+4*30*Nd
        for i in range(Nd*3):
            if line[k]=="1":
                g.paste(x+d1+d2+5*di+di*i+il*dj, y-d1-d2-5*di-di*i+il*dj, "or")
            k+=1
        d3 = (3*N)*dj2-1110+300+900+6*30
        for i in range(M):
            if line[k]=="1":
                g.paste(x+d1+d2+d3+(5+Nd*3)*di+17*30*i+il*dj, y-d1-d2-d3-(5+Nd*3)*di-17*30*i+il*dj, "or")
            k+=1

def paste(file, x, y):
    g.addlayer()
    g.open(file)
    rect = g.getrect()
    g.select(rect)
    g.copy()
    g.dellayer()
    g.paste(x,y,'or')

def rm_line(x, y, dx, dy, w, N):
    for i in range(N):
        g.select([x+i*dx,y+i*dy,w,w])
        g.clear(0)
Nd = int(math.log(N,2))
Pd = int(math.log(P,2))
data = assemble(preprocess(program))
print(list(preprocess(program)))

g.addlayer()

dj2 = 2*30
di2 = 60*Nd
left_input_x = -(3*N-1)*di2-(3*N-1)*dj2-900-500+123 + (3*Nd)*-4*30
left_input_y = -(3*N-1)*di2+(3*N-1)*dj2-300+73 + (3*Nd)*4*30
x,y = left_input_x-4*30*Nd, left_input_y+4*30*Nd
hm2 = 30*24*N+120*Nd + 5*30 # height of the memory
wm = 30*17*M #width of the memory
walu = 1650*M+600
halu = 60*2*M+30*70 # left height of the alu
hp = 60*Pd*P
f = "patterns/computer_{}_{}_{}.mc".format(N,M,P)
g.show(f)
g.open(f)
data = assemble(preprocess(program))
write_program(x-60*Pd*(P-1)-14274-249-240,y-60*Pd*(P-1)-6556-227+240, data)
if "disp" in program:
    paste('display.mc', halu+hm2+wm+M*60+438+3000, halu+hm2-wm+M*60-9487-3000)
    rm_line(halu+hm2+wm+M*60+1200-8*30, halu+hm2-wm+M*60+600-1-8*30, 4*30, 4*30, 100, 12)
g.save("programed.mc", 'mc')
