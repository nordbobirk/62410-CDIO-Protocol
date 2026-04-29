"""
PENIS unit tests
Run: python -m unittest test_protocol.py
"""
import unittest
from protocol import (
    CommandName, Instruction, Arguments, InstructionType,
    serialize_message, parse_message, serialize_arguments,
    Message, Acknowledgement, serialize_ack, parse_ack,
    parse_arguments, SequenceName, RequestName
)

class TestPENISProtocol(unittest.TestCase):
    
    def assert_default_arguments(self, arguments):
        expected = Arguments()
        self.assertEqual(arguments.inst_id, expected.inst_id)
        self.assertEqual(arguments.rspeed, expected.rspeed)
        self.assertEqual(arguments.lspeed, expected.lspeed)
        self.assertEqual(arguments.speed, expected.speed)
        self.assertEqual(arguments.rotations, expected.rotations)
        self.assertEqual(arguments.position, expected.position)
        self.assertEqual(arguments.seconds, expected.seconds)
        self.assertEqual(arguments.target_angle, expected.target_angle)
        self.assertEqual(arguments.brake, expected.brake)
        self.assertEqual(arguments.block, expected.block)
        self.assertEqual(arguments.talk, expected.talk)

    # region serialization

    def test_serialize_arguments(self):
        arguments = Arguments()
        serialized = serialize_arguments(arguments)
        self.assertEqual(serialized, ";20;20;20;5.0;10;1;0;True;False;")

        custom_arguments = Arguments(
            inst_id="",
            rspeed=0,
            lspeed=0,
            speed=0,
            rotations=0.0,
            position=0,
            seconds=0,
            target_angle=360,
            brake=False,
            block=True,
            talk="yeet",
        )
        custom_serialized = serialize_arguments(custom_arguments)
        self.assertEqual(custom_arguments.rspeed, 0)
        self.assertEqual(custom_serialized, ";0;0;0;0.0;0;0;360;False;True;yeet")

    def test_serialize_message(self):
        message = Message(instruction = Instruction(name = CommandName.FORWARD, type = InstructionType.COMMAND, args = Arguments()))
        serialized = serialize_message(message)
        self.assertEqual(serialized, "c_fwd:;20;20;20;5.0;10;1;0;True;False;")

    def test_serialize_ack(self):
        ack = Acknowledgement("ACK", { "key": "value" })
        serialized_ack = serialize_ack(ack)
        self.assertEqual(serialized_ack, "ACK {\"key\": \"value\"}")

        nak = Acknowledgement("NAK", { "key": "value"} )
        serialized_nak = serialize_ack(nak)
        self.assertEqual(serialized_nak, "NAK {\"key\": \"value\"}")

        ack_no_data = Acknowledgement("ACK")
        serialized_ack_no_data = serialize_ack(ack_no_data)
        self.assertEqual(serialized_ack_no_data, "ACK {}")

        nak_no_data = Acknowledgement("NAK")
        serialized_nak_no_data = serialize_ack(nak_no_data)
        self.assertEqual(serialized_nak_no_data, "NAK {}")

    # endregion serialization

    # region parsing

    def test_parse_arguments(self):
        serialized = ";20;20;20;5.0;10;1;0;True;False;"
        arguments = parse_arguments(serialized.split(";"))
        self.assert_default_arguments(arguments)

        custom_arguments = Arguments(
            inst_id="",
            rspeed=0,
            lspeed=0,
            speed=0,
            rotations=0.0,
            position=0,
            seconds=0,
            target_angle=360,
            brake=False,
            block=True,
            talk="yeet",
        )
        custom_serialized = serialize_arguments(custom_arguments)
        self.assertEqual(custom_arguments.rspeed, 0)
        self.assertEqual(custom_serialized, ";0;0;0;0.0;0;0;360;False;True;yeet")
    
    def test_parse_message(self):
        serialized_message = "c_fwd:;20;20;20;5.0;10;1;0;True;False;"
        message = parse_message(serialized_message)
        instruction = message.instruction
        arguments = instruction.args
        self.assertEqual(instruction.name, CommandName.FORWARD)
        self.assertEqual(instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(arguments)
    
    def test_parse_acknowledgement(self):
        serialized_ack = "ACK {\"key\": \"value\"}"
        ack = parse_ack(serialized_ack)
        expected = Acknowledgement("ACK", { "key": "value" })
        self.assertEqual(ack.status, expected.status)
        self.assertEqual(ack.data, expected.data)

        serialized_nak = "NAK {\"key\": \"value\"}"
        nak = parse_ack(serialized_nak)
        expected = Acknowledgement("NAK", { "key": "value"} )
        self.assertEqual(nak.status, expected.status)
        self.assertEqual(nak.data, expected.data)

        serialized_ack_no_data = "ACK {}"
        ack_no_data = parse_ack(serialized_ack_no_data)
        expected = Acknowledgement("ACK")
        self.assertEqual(ack_no_data.status, expected.status)
        self.assertEqual(ack_no_data.data, expected.data)

        serialized_nak_no_data = "NAK {}"
        nak_no_data = parse_ack(serialized_nak_no_data)
        expected = Acknowledgement("NAK")
        self.assertEqual(nak_no_data.status, expected.status)
        self.assertEqual(nak_no_data.data, expected.data)

    # endregion parsing

    # region roundtrip

    def test_roundtrip_forward(self):
        inst = Instruction(
            name = CommandName.FORWARD,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.FORWARD)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)

    def test_roundtrip_backward(self):
        inst = Instruction(
            name = CommandName.BACKWARD,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.BACKWARD)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_tank_left(self):
        inst = Instruction(
            name = CommandName.TANK_LEFT,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.TANK_LEFT)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_tank_right(self):
        inst = Instruction(
            name = CommandName.TANK_RIGHT,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.TANK_RIGHT)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_ball_in(self):
        inst = Instruction(
            name = CommandName.BALL_IN,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.BALL_IN)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_ball_out(self):
        inst = Instruction(
            name = CommandName.BALL_OUT,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.BALL_OUT)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_ball_off(self):
        inst = Instruction(
            name = CommandName.BALL_OFF,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.BALL_OFF)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_talk(self):
        inst = Instruction(
            name = CommandName.TALK,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, CommandName.TALK)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_panic(self):
        inst = Instruction(
            name = CommandName.PANIC,
            type = InstructionType.COMMAND,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)

        self.assertEqual(res.instruction.name, CommandName.PANIC)
        self.assertEqual(res.instruction.type, InstructionType.COMMAND)
        self.assert_default_arguments(res.instruction.args)

    def test_roundtrip_eject(self):
        inst = Instruction(
            name = SequenceName.EJECT,
            type = InstructionType.SEQUENCE,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, SequenceName.EJECT)
        self.assertEqual(res.instruction.type, InstructionType.SEQUENCE)
        self.assert_default_arguments(res.instruction.args)
    
    def test_roundtrip_request(self):
        inst = Instruction(
            name = "ev3_attr",
            type = InstructionType.REQUEST,
            args = Arguments()
        )
        msg = Message(instruction = inst)
        smsg = serialize_message(message = msg)
        res = parse_message(smsg)
        
        self.assertEqual(res.instruction.name, "ev3_attr")
        self.assertEqual(res.instruction.type, InstructionType.REQUEST)
        self.assert_default_arguments(res.instruction.args)

    # endregion roundtrip

    # region validation

    def test_argument_validation(self):
        with self.assertRaises(ValueError) as ctx:
            Arguments(inst_id = "not empty")
        self.assertTrue("Instruction id is currently reserved and must be an empty string" in str(ctx.exception))
        Arguments(inst_id = "") # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(rspeed = -101)
        self.assertTrue("Right speed must be within [-100;100], received -101" in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Arguments(rspeed = 101)
        self.assertTrue("Right speed must be within [-100;100], received 101" in str(ctx.exception))
        Arguments(rspeed = 0) # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(lspeed = -101)
        self.assertTrue("Left speed must be within [-100;100], received -101" in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Arguments(lspeed = 101)
        self.assertTrue("Left speed must be within [-100;100], received 101" in str(ctx.exception))
        Arguments(lspeed = 0) # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(speed = -101)
        self.assertTrue("Speed must be within [-100;100], received -101" in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Arguments(speed = 101)
        self.assertTrue("Speed must be within [-100;100], received 101" in str(ctx.exception))
        Arguments(speed = 0) # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(seconds = -1)
        self.assertTrue("Seconds must be a non-negative integer, received -1" in str(ctx.exception))
        Arguments(seconds = 0) # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(target_angle = -361)
        self.assertTrue("Target angle must be within [-360;360], received -361" in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Arguments(target_angle = 361)
        self.assertTrue("Target angle must be within [-360;360], received 361" in str(ctx.exception))
        Arguments(target_angle = 0) # happy path

        with self.assertRaises(ValueError) as ctx:
            Arguments(talk = ":")
        self.assertTrue("Talk must only include alphanumeric characters as well as the dot, comma, and space characters." in str(ctx.exception))
        Arguments(talk = "talk") # happy path
    
    def test_instruction_validation(self):
        with self.assertRaises(ValueError) as ctx:
            Instruction(name = CommandName.FORWARD, type = "unknown-type", args = Arguments())
        self.assertTrue("Instruction type must be an InstructionType member, got unknown-type." in str(ctx.exception))
        Instruction(name = CommandName.FORWARD, type = InstructionType.COMMAND, args = Arguments()) # happy path

        with self.assertRaises(ValueError) as ctx:
            Instruction(name = "unknown-command", type = InstructionType.COMMAND, args = Arguments())
        self.assertTrue("Command instruction name must be a CommandName member, got unknown-command." in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Instruction(name = SequenceName.EJECT, type = InstructionType.COMMAND, args = Arguments())
        self.assertTrue("Command instruction name must be a CommandName member, got SequenceName.EJECT" in str(ctx.exception))
        Instruction(name = CommandName.FORWARD, type = InstructionType.COMMAND, args = Arguments()) # happy path

        with self.assertRaises(ValueError) as ctx:
            Instruction(name = "unknown-sequence", type = InstructionType.SEQUENCE, args = Arguments())
        self.assertTrue("Sequence instruction name must be a SequenceName member, got unknown-sequence" in str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            Instruction(name = CommandName.FORWARD, type = InstructionType.SEQUENCE, args = Arguments())
        self.assertTrue("Sequence instruction name must be a SequenceName member, got CommandName.FORWARD" in str(ctx.exception))
        Instruction(name = SequenceName.EJECT, type = InstructionType.SEQUENCE, args = Arguments()) # happy path

        with self.assertRaises(ValueError) as ctx:
            Instruction(name = "not-a-request", type = InstructionType.REQUEST, args = Arguments())
        self.assertTrue("Unknown request name not-a-request, missing prefix." in str(ctx.exception))
        Instruction(name = "ev3_attribute", type = InstructionType.REQUEST, args = Arguments()) # happy path
    
    def test_acknowledgement_validation(self):
        with self.assertRaises(ValueError) as ctx:
            Acknowledgement(status = "not-a-status")
        self.assertTrue("Unknown status not-a-status, expect 'ACK' or 'NAK'." in str(ctx.exception))
        Acknowledgement(status = "ACK") # happy path
        Acknowledgement(status = "NAK") # happy path

        with self.assertRaises(ValueError) as ctx:
            Acknowledgement("ACK", Arguments())
        self.assertTrue("Data must be valid JSON." in str(ctx.exception))
        Acknowledgement(status = "ACK", data = { "key": "value" }) # happy path

    # endregion validation

#region requests
def test_roundtrip_request_speed(self):
    inst = Instruction(
        name = RequestName.SPEED.value,
        type = InstructionType.REQUEST,
        args = Arguments()
    )
    msg = Message(instruction = inst)
    smsg = serialize_message(message = msg)
    res = parse_message(smsg)

    self.assertEqual(res.instruction.name, RequestName.SPEED.value)
    self.assertEqual(res.instruction.type, InstructionType.REQUEST)
    self.assert_default_arguments(res.instruction.args)


def test_roundtrip_request_isrunning(self):
    inst = Instruction(
        name = RequestName.ISRUNNING.value,
        type = InstructionType.REQUEST,
        args = Arguments()
    )
    msg = Message(instruction = inst)
    smsg = serialize_message(message = msg)
    res = parse_message(smsg)

    self.assertEqual(res.instruction.name, RequestName.ISRUNNING.value)
    self.assertEqual(res.instruction.type, InstructionType.REQUEST)
    self.assert_default_arguments(res.instruction.args)


def test_roundtrip_request_isholding(self):
    inst = Instruction(
        name = RequestName.ISHOLDING.value,
        type = InstructionType.REQUEST,
        args = Arguments()
    )
    msg = Message(instruction = inst)
    smsg = serialize_message(message = msg)
    res = parse_message(smsg)

    self.assertEqual(res.instruction.name, RequestName.ISHOLDING.value)
    self.assertEqual(res.instruction.type, InstructionType.REQUEST)
    self.assert_default_arguments(res.instruction.args)


def test_roundtrip_request_isramping(self):
    inst = Instruction(
        name = RequestName.ISRAMPING.value,
        type = InstructionType.REQUEST,
        args = Arguments()
    )
    msg = Message(instruction = inst)
    smsg = serialize_message(message = msg)
    res = parse_message(smsg)

    self.assertEqual(res.instruction.name, RequestName.ISRAMPING.value)
    self.assertEqual(res.instruction.type, InstructionType.REQUEST)
    self.assert_default_arguments(res.instruction.args)


def test_roundtrip_request_isoverloaded(self):
    inst = Instruction(
        name = RequestName.ISOVERLOADED.value,
        type = InstructionType.REQUEST,
        args = Arguments()
    )
    msg = Message(instruction = inst)
    smsg = serialize_message(message = msg)
    res = parse_message(smsg)

    self.assertEqual(res.instruction.name, RequestName.ISOVERLOADED.value)
    self.assertEqual(res.instruction.type, InstructionType.REQUEST)
    self.assert_default_arguments(res.instruction.args)

def test_request_name_enum_values(self):
    self.assertEqual(RequestName.SPEED.value, "speed")
    self.assertEqual(RequestName.ISRUNNING.value, "isRunning")
    self.assertEqual(RequestName.ISHOLDING.value, "isHolding")
    self.assertEqual(RequestName.ISRAMPING.value, "isRamping")
    self.assertEqual(RequestName.ISOVERLOADED.value, "isOverloaded")

def test_instruction_validation_request_enum_names(self):
    with self.assertRaises(ValueError) as ctx:
        Instruction(name = RequestName.SPEED.value, type = InstructionType.REQUEST, args = Arguments())
    self.assertTrue("Unknown request name speed, missing prefix." in str(ctx.exception))
#endregion requests


if __name__ == '__main__':
    unittest.main()
