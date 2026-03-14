# Protocol for Efficient Navigation and Intercommunication Sequences specification
This file contains the specification for the PENIS.

## General
This is an application layer protocol, which is intended to run on top of TCP, thus avoiding the complexities of having to implement reliability guarantees. The protocol handles communication between one Lego Mindstorm EV3 robot and the robot controller, which instructs the robot what to do based on camera input and image recognition. Communication is always initiated by the controller, which sends *messages* to the robot, and the robot responds to the messages with [acknowledgements](#acknowledgements).

## Instructions
An instruction is a unit of work to be carried out by the robot. It can be one of three types: a [*command*](#commands), a [*sequence*](#sequences) or a [*request*](#requests). A command is an atomic unit of work, for instance moving forward. A sequence is a sequence of instructions that is pre-programmed in the robot. A request is a an instruction that doesn't cause the robot to do any actions but instead returns some data from the robot as JSON. In PENIS, it is possible to send multiple instructions in one message (see [message syntax](#message-syntax)).To distinguish between commands, sequences and requests when transmitting messages from the controller to the robot, each instruction is prefixed:
- command prefix: `c_ `
- sequence prefix: `s_ `
- request prefix: `r_ `

### Commands
Commands are atomic units of work to be carried out by the robot. PENIS includes the following commands:
- forward (`fwd`): instructs the robot to drive forwards according to the given arguments.
- backward (`bwd`): instructs the robot to drive backwards according to the given arguments.
- tank left (`tl`): instructs the robot to turn left using tank steering according to the given arguments.
- tank right (`tr`): instructs the robot to turn right using tank steering according to the given arguments.
- ball in (`bin`): instructs the robot to turn the ball collecting wheels inwards.
- ball out (`bout`): instructs the robot to turn the ball collecting wheels outwards.
- ball off (`boff`): instructs the robot to stop the ball collecting wheels.
- talk (`t`): instructs the robot to talk according to the given arguments.

### Sequences
Sequences are pre-programmed sequences of instructions that the robot knows by a sequence name. PENIS includes the following sequences:
- eject (`bust`): instructs the robot to run the ball ejection sequence.

### Requests
Requests are instructions that query the robot for information without causing it to perform any physical action. Requests can be used to query any stateful information in the robot. We refer to these stateful values in the robot as *attributes*. The syntax of a request is `ev3_<attribute>`, where `<attribute>` is the attribute to query.

### Instruction arguments
All [instructions](#instructions) accept so-called *arguments* as input. Every instruction accepts ALL arguments that are defined in PENIS; even if an instruction does not use an argument, space is reserved for it in the argument section of the message body. The following arguments are defined in PENIS:
1. Instruction id (`inst_id`) (unique identifyer for this particular instruction instance).
2. Right speed percent (`rspeed`): speed of right wheels in percent of maximum possible speed.
3. Left speed percent (`lspeed`): speed of left wheels in percent of maximum possible speed.
4. Speed percent (`speed`): speed of both sets of wheels in perceot of maximum possible speed.
5. Rotations (`rotations`): 
6. Position (`position`): 
7. Seconds (`seconds`): the amount of seconds for which to turn on some motor.
8. Degrees (`degrees`): 
9. Brake (`brake`): whether or not to brake after moving (boolean).
10. Block (`block`): whether or not the command should block, meaning it can not be interrupted by other instructions (boolean).
11. Talk (`talk`): a message for the robot to say.

## Acknowledgements
Each message sent from the controller to the robot has a corresponding response, which consists of one or more *acknowledgements*. For most instructions, this is a simple positive or negative acknowledgement, but for [requests](#requests) it also includes the requested data. The syntax of a positive acknowledgement is `ACK <inst_id> <data>` where `ACK` is the ASCII acknowledgement character, `<inst_id>` is the unique identifyer of the instruction, and `<data>` is a stringified JSON object. For most instructions, this is just an empty object, but for requests, it contains the requested data. The syntax of a negative acknowledgement is `NAK <inst_id> <data>`, where `NAK` is the ASCII negative acknowledgement character, `<inst_id>` is the unique identifyer of the instruction, and `<data>` is an empty stringified JSON object, which is included to allow data transfer in negative acknowledgements in future versions of PENIS.

When the robot receives a message, it parses each instruction. If an instruction is invalid or unknown, a negative acknowledgement for it is returned. Otherwise, the robot carries out the required action and responds with a positive acknowledgement. Thus, acknowledgements are per-instruction and not per-message and allow the controller to know what the robot has done and what it has not yet done.

## Message syntax
A message, which is an instance of communication between from the controller to the robot, has the following syntax:

`<instruction>&...&<instruction>`

Each `<instruction>` is a full instruction, including the fully qualified (including prefix) instruction name and the arguments. Multiple instructions are separated by `&`. There is no ampersand after the last instruction in the message. Each `<instruction>` has the following syntax:

`<inst_name>:<inst_id>;<rspeed>;<lspeed>;<speed>;<rotation>;<position>;<seconds>;<degrees>;<brake>;<block>;<talk>`

The instruction name is separated from the arguments by `:`, and each argument is separated by `;`. There is no semi colon after the last argument to the instruction.
