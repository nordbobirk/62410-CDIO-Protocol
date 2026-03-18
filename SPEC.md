# Protocol for Efficient Navigation and Intercommunication Sequences specification
This file contains the specification for the PENIS.

## General
This is an application layer protocol, which is intended to run on top of TCP, thus avoiding the complexities of having to implement reliability guarantees. The protocol handles communication between one Lego Mindstorm EV3 robot and the robot controller, which instructs the robot what to do based on camera input and image recognition. Communication is always initiated by the controller, which sends *messages* to the robot, and the robot responds to the messages with [acknowledgements](#acknowledgements).

## Instructions
An instruction is a unit of work to be carried out by the robot. It can be one of three types: a [*command*](#commands), a [*sequence*](#sequences) or a [*request*](#requests). A command is an atomic unit of work, for instance moving forward. A sequence is a sequence of instructions that is pre-programmed in the robot. A request is an instruction that doesn't cause the robot to do any actions but instead returns some data from the robot as JSON. To distinguish between commands, sequences and requests when transmitting messages from the controller to the robot, each instruction is prefixed:
- command prefix: `c_`
- sequence prefix: `s_`
- request prefix: `r_`

### Commands
Commands are atomic units of work to be carried out by the robot. PENIS includes the following commands:
- forward (`fwd`): instructs the robot to drive forwards according to the given arguments. This command accepts the following arguments (others are ignored): 
    - `speed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
        3. `position`
    - `brake`
    - `block`
- backward (`bwd`): instructs the robot to drive backwards according to the given arguments. This command accepts the following arguments (others are ignored): 
    - `speed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
        3. `position`
    - `brake`
    - `block`
- tank left (`tl`): instructs the robot to turn left using tank steering according to the given arguments. This command accepts the following arguments (others are ignored): 

    Gyro turn
    - `speed` 
    - `target_angle`

    OR

    Tank turn
    - `lspeed`
    - `rspeed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
        3. `position`

    AND

    - `brake`
    - `block`
- tank right (`tr`): instructs the robot to turn right using tank steering according to the given arguments. This command accepts the following arguments (others are ignored): 

    Gyro turn
    - `speed` 
    - `target_angle`

    OR

    Tank turn
    - `lspeed`
    - `rspeed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
        3. `position`

    AND

    - `brake`
    - `block`
- ball in (`bin`): instructs the robot to turn the ball collecting wheels inwards. This command accepts the following arguments (others are ignored): 
    - `speed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
    - `brake`
    - `block`
- ball out (`bout`): instructs the robot to turn the ball collecting wheels outwards. This command accepts the following arguments (others are ignored): 
    - `speed`
    - A form of duration of activation:
        1. `seconds`
        2. `rotations`
        3. `position`
    - `brake`
    - `block`
- ball off (`boff`): instructs the robot to stop the ball collecting wheels. This command accepts the following arguments (others are ignored): 
    - `brake`
    - `block`
- talk (`t`): instructs the robot to talk according to the given arguments. This command accepts the following arguments (others are ignored): 
    - `talk`

#### Note
The precedence of the arguments with the same usage (mainly rotations, positions, seconds & left, right speed) is equal to the order above. For example, if `speed` is provided the gyro functionality will be used, otherwise the regular tank turning will be used with the `lspeed` & `rspeed`. If multiple arguments are given, the argument with the highest precedence is used, and the rest are ignored.

### Sequences
Sequences are pre-programmed sequences of instructions that the robot knows by a sequence name. PENIS includes the following sequences:
- eject (`bust`): instructs the robot to run the ball ejection sequence.

Note that sequences don't use any arguments.

### Requests
Requests are instructions that query the robot for information without causing it to perform any physical action. Requests can be used to query any stateful information in the robot. We refer to these stateful values in the robot as *attributes*. The syntax of a request is `ev3_<attribute>`, where `<attribute>` is the attribute to query.

### Instruction arguments
All [instructions](#instructions) accept so-called *arguments* as input. Every instruction accepts ALL arguments that are defined in PENIS; even if an instruction does not use an argument, space is reserved for it in the argument section of the message body. If a command doesn't use an argument, an empty string is placed in that arguments place. The following arguments are defined in PENIS:
1. Instruction id (`inst_id`) (unique identifier for this particular instruction instance). This argument is not used but is reserved for future use, so the controller sends an empty string in this argument.
2. Right speed percent (`rspeed`): speed of right wheels in percent of maximum possible speed. This is an integer in the range `[-100;100]`. Default: `20`.
3. Left speed percent (`lspeed`): speed of left wheels in percent of maximum possible speed. This is an integer in the range `[-100;100]`. Default: `20`.
4. Speed percent (`speed`): speed of both sets of wheels in percent of maximum possible speed. This is an integer in the range `[-100;100]`. Default: `20`.
5. Rotations (`rotations`): rotations per minute of the wheels. This is a signed integer. Default: `5`.
6. Position (`position`): in short, position describes the current position of the motor in pulses of the rotary encoder. When the motor rotates clockwise, the position will increase. Likewise, rotating counter-clockwise causes the position to decrease. Default: `10`.
7. Seconds (`seconds`): the amount of seconds for which to turn on some motor. This is a non-negative integer. Default: `1`.
8. Target angle (`target_angle`): the target angle for a turn. Requires a gyro sensor for measuring the rotation on the plane of rotation of the gyro. This is a signed integer in the range `[-360; 360]`. Default: `0`.
9. Brake (`brake`): whether or not to brake after moving (either `true` or `false`). Default: `true`.
10. Block (`block`): whether or not the instruction should block (either `true` or `false`). If an instruction is blocking, then other instructions arriving during execution of the blocking instruction will be queued and carried out after execution of the blocking instruction completes. If an instruction is not blocking, then other instructions arriving during execution of the non-blocking instruction will interrupt and begin execution immediately. Default: `false`.
11. Talk (`talk`): a message for the robot to say. This is a string that must match this regex: /^[a-zA-Z0-9\.\,\ ]*$/. Default: `""`.

For more details on certain values like `position`, see the official python-ev3dev motor [documentation](https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/ev3dev-stretch/motors.html#units): 

It should be noted that there are three semantically overlapping speed arguments. However, commands will either only use one type or define precedence on a per-command basis (see [commands specification](#commands)).

PENIS does not specify any arguments to be required; instead, default values for all arguments are defined. Thus, it is the responsibility of the controller to input the needed arguments to achieve the intended function. If the robot requires an argument for execution and the argument is not given, the default values is used as specified above.

## Acknowledgements
Each message sent from the controller to the robot results in a corresponding acknowledgement being sent from the robot to the controller. The acknowledgement is either positive or negative. A positive acknowledgement has the following syntax:

`ACK <data>\n`

where `<data>` is a stringified JSON object containing the requests data if the instruction is a request, and otherwise a stringified empty JSON object.

A negative acknowledgement has the following syntax:

`NAK <data>\n`

where `<data>` is a stringified empty JSON object, which is included to allow transmission of key-value data in negative acknowledgements in the future.

Semantically, a negative acknowledgement means that the robot does not understand the instruction, meaning there is likely a syntax error. A positive acknowledgement has the semantic meaning that the robot understands the instruction and will carry out the requested action as soon as possible. Thus, positive acknowledgements might be sent before the action has been carried out by the robot.

## Message syntax
A message, which is an instance of communication from the controller to the robot, has the following syntax:

`<instruction>\n`

where `<instruction>` is a full instruction, including the fully qualified (including prefix) instruction name and the arguments. An `<instruction>` has the following syntax:

`<inst_name>:<inst_id>;<rspeed>;<lspeed>;<speed>;<rotations>;<position>;<seconds>;<target_angle>;<brake>;<block>;<talk>`

The instruction name is separated from the arguments by `:`, and each argument is separated by `;`. There is no semicolon after the last argument to the instruction.
