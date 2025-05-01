# THIS CODE WAS AUTOMATICALLY GENERATED, DO NOT MODIFY
# ruff: noqa

import math
import struct

# Simulated data stores. In a real application these would be updated dynamically.
COILS = [False] * 1000  # list of 1000 coils, all False initially
DISCRETE_INPUTS = [False] * 1000  # list of discrete inputs
HOLDING_REGISTERS = [0] * 1000  # 1000 registers, 16‐bit values
INPUT_REGISTERS = [0] * 1000  # 1000 input registers


class ModbusException(Exception):
    def __init__(self, function_code, error_code, message="Modbus error"):
        self.function_code = function_code
        self.error_code = error_code
        super().__init__(message)


def pack_bits(bits):
    """Pack a list of booleans into bytes (LSB first)."""
    nbytes = math.ceil(len(bits) / 8)
    out = bytearray(nbytes)
    for i, bit in enumerate(bits):
        if bit:
            out[i // 8] |= 1 << (i % 8)
    return bytes(out)


def process_modbus_request(request: bytes) -> bytes:
    """
    Process a Modbus TCP request.
    The request is assumed to follow the format:
      Transaction ID (2 bytes)
      Protocol ID (2 bytes)
      Length (2 bytes) -> (# bytes to follow in UnitID + PDU)
      Unit Identifier (1 byte)
      PDU: Function Code (1 byte) + Data (n bytes)
    If anything goes wrong, raise an Exception.
    """

    try:
        # The MBAP header is 7 bytes total.
        if len(request) < 7:
            raise ValueError("Request too short to contain MBAP header")

        # Unpack MBAP header: Transaction ID, Protocol ID, Length, UnitID
        transaction_id, protocol_id, length = struct.unpack(">HHH", request[0:6])
        # Check that request length is consistent
        if len(request) != 6 + length:
            raise ValueError("MBAP length inconsistent with actual request length")
        unit_id = request[6]
        # The remaining bytes are the PDU:
        pdu = request[7:]
        if len(pdu) < 1:
            raise ValueError("PDU missing function code")

        # Parse function code
        function_code = pdu[0]
        data = pdu[1:]

        # Prepare storage for response PDU components
        response_pdu = b""

        # ---- Process supported function codes ----
        if function_code == 0x01:  # Read Coils
            if len(data) != 4:
                raise ValueError("Invalid data length for Read Coils")
            # Unpack starting address and quantity (big-endian)
            start_addr, quantity = struct.unpack(">HH", data)
            # simple range-check (addresses 0 to length-1)
            if start_addr + quantity > len(COILS):
                # Exception code 0x02: Illegal Data Address
                raise ModbusException(function_code, 0x02, "Address out of range")
            # Get the coil states for the request
            coil_values = COILS[start_addr : start_addr + quantity]
            # Pack bits into bytes
            coil_bytes = pack_bits(coil_values)
            byte_count = len(coil_bytes)
            response_pdu = struct.pack("BB", function_code, byte_count) + coil_bytes

        elif function_code == 0x02:  # Read Discrete Inputs
            if len(data) != 4:
                raise ValueError("Invalid data length for Read Discrete Inputs")
            start_addr, quantity = struct.unpack(">HH", data)
            if start_addr + quantity > len(DISCRETE_INPUTS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            inputs = DISCRETE_INPUTS[start_addr : start_addr + quantity]
            inputs_bytes = pack_bits(inputs)
            byte_count = len(inputs_bytes)
            response_pdu = struct.pack("BB", function_code, byte_count) + inputs_bytes

        elif function_code == 0x03:  # Read Holding Registers
            if len(data) != 4:
                raise ValueError("Invalid data length for Read Holding Registers")
            start_addr, quantity = struct.unpack(">HH", data)
            if start_addr + quantity > len(HOLDING_REGISTERS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            regs = HOLDING_REGISTERS[start_addr : start_addr + quantity]
            byte_count = quantity * 2
            regs_payload = b"".join(struct.pack(">H", reg) for reg in regs)
            response_pdu = struct.pack("BB", function_code, byte_count) + regs_payload

        elif function_code == 0x04:  # Read Input Registers
            if len(data) != 4:
                raise ValueError("Invalid data length for Read Input Registers")
            start_addr, quantity = struct.unpack(">HH", data)
            if start_addr + quantity > len(INPUT_REGISTERS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            regs = INPUT_REGISTERS[start_addr : start_addr + quantity]
            byte_count = quantity * 2
            regs_payload = b"".join(struct.pack(">H", reg) for reg in regs)
            response_pdu = struct.pack("BB", function_code, byte_count) + regs_payload

        elif function_code == 0x05:  # Write Single Coil
            if len(data) != 4:
                raise ValueError("Invalid data length for Write Single Coil")
            addr, value = struct.unpack(">HH", data)
            if addr >= len(COILS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            # Per Modbus, a non-zero value (usually 0xff00) is ON; else OFF.
            COILS[addr] = value == 0xFF00
            # Standard response echoes request
            response_pdu = struct.pack("B", function_code) + data

        elif function_code == 0x06:  # Write Single Register
            if len(data) != 4:
                raise ValueError("Invalid data length for Write Single Register")
            addr, value = struct.unpack(">HH", data)
            if addr >= len(HOLDING_REGISTERS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            HOLDING_REGISTERS[addr] = value
            # Echo the request in the response
            response_pdu = struct.pack("B", function_code) + data

        elif function_code == 0x0F:  # Write Multiple Coils
            # PDU format: starting addr (2), quantity of coils (2), byte count (1), coil data (N bytes)
            if len(data) < 5:
                raise ValueError("Invalid data length for Write Multiple Coils")
            start_addr, quantity, byte_count = struct.unpack(">HHB", data[0:5])
            if len(data[5:]) != byte_count:
                raise ValueError("Mismatch between byte count and provided coil data")
            if start_addr + quantity > len(COILS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            # Unpack coil values from the byte array:
            coil_data = []
            bits = []
            for byte in data[5:]:
                for i in range(8):
                    bits.append(bool(byte & (1 << i)))
            coil_data = bits[:quantity]
            # Write them to our simulated coil storage:
            for i, val in enumerate(coil_data):
                COILS[start_addr + i] = val
            # Response echoes starting address and quantity:
            response_pdu = struct.pack(">BHH", function_code, start_addr, quantity)

        elif function_code == 0x10:  # Write Multiple Registers
            # PDU format: starting addr (2), quantity (2), byte count (1), registers (N bytes)
            if len(data) < 5:
                raise ValueError("Invalid data length for Write Multiple Registers")
            start_addr, quantity, byte_count = struct.unpack(">HHB", data[0:5])
            if byte_count != quantity * 2 or len(data[5:]) != byte_count:
                raise ValueError("Byte count does not match register quantity")
            if start_addr + quantity > len(HOLDING_REGISTERS):
                raise ModbusException(function_code, 0x02, "Address out of range")
            regs = []
            for i in range(quantity):
                reg_val = struct.unpack(">H", data[5 + i * 2 : 5 + i * 2 + 2])[0]
                regs.append(reg_val)
                HOLDING_REGISTERS[start_addr + i] = reg_val
            # Response echoes starting address and quantity:
            response_pdu = struct.pack(">BHH", function_code, start_addr, quantity)

        elif function_code == 0x11:  # Report Slave ID
            # For demonstration, we reply with a slave id (1 byte) and a run indicator status (1 byte)
            slave_identifier = unit_id  # In this demo we simply use the unit id.
            run_indicator = 0xFF  # for example, 'on'
            additional_data = b"Demo Device"  # Can be any additional information.
            byte_count = 2 + len(additional_data)
            response_pdu = (
                struct.pack("BB", function_code, byte_count)
                + struct.pack("BB", slave_identifier, run_indicator)
                + additional_data
            )

        else:
            # If the function code isn’t recognized or supported, raise an exception.
            raise ModbusException(function_code, 0x01, "Illegal Function")

    except Exception as e:
        # In case of error, build an exception response per Modbus spec.
        # The exception function code is original function code OR-ed with 0x80.
        if isinstance(e, ModbusException):
            err_func = e.function_code | 0x80
            err_code = e.error_code
        else:
            err_func = (function_code if "function_code" in locals() else 0) | 0x80
            err_code = 0x04  # Slave Device Failure (example use)
        response_pdu = struct.pack("BB", err_func, err_code)

    # Build the full MBAP header.
    # The Length field is the number of bytes following the length field (unit id + response PDU).
    unit_id_byte = struct.pack("B", unit_id)
    pdu_length = len(unit_id_byte) + len(response_pdu)
    mbap = struct.pack(">HHH", transaction_id, protocol_id, pdu_length)
    response_packet = mbap + unit_id_byte + response_pdu
    return response_packet


# Example usage:
if __name__ == "__main__":
    # Example request in hex:
    # 79 56 00 00 00 06 01 01 00 0f 00 16
    # Which in bytes:
    request_bytes = bytes.fromhex("79 56 00 00 00 06 01 01 00 0f 00 16")
    try:
        response = process_modbus_request(request_bytes)
        print("Response (hex):", response.hex(" "))
    except Exception as ex:
        print("Error processing request:", ex)
