#!/usr/bin/python3

import datetime
import re
import serial
import time

INIT_CMD = [
    b'ATZ',
    b'ATSH FC007B',
    b'ATCP 17',
    b'ATCAF0',
    b'ATCRA17FE007B'
]

INIT_CMD2 = [
    b'ATSH FC0076',
    b'ATCRA17FE0076'
]

CMDS = [
    b'22465b',
    b'22465d',
    b'227448',
    b'22743b',
    b'221e33',
    b'221e34',
    b'221e40',
    b'221e49',
    b'221ea3',
    b'221ea4',
    b'221ea5',
    b'221ea6',
    b'221ea7',
    b'221ea8',
    b'221ea9',
    b'221eaa',
    b'221eab',
    b'221e4a',
    b'221e4b',
    b'221e4c',
    b'221e4d',
    b'221e4e',
    b'221e4f',
    b'221e50',
    b'221e51',
    b'221e52',
    b'221e41',
    b'221e53',
    b'221e54',
    b'221e55',
    b'221e56',
    b'221e57',
    b'221e58',
    b'221e59',
    b'221e5a',
    b'221e5b',
    b'221e5c',
    b'221e42',
    b'221e5d',
    b'221e5e',
    b'221e5f',
    b'221e60',
    b'221e61',
    b'221e62',
    b'221e63',
    b'221e64',
    b'221e65',
    b'221e66',
    b'221e43',
    b'221e67',
    b'221e67',
    b'221e68',
    b'221e6a',
    b'221e6b',
    b'221e6c',
    b'221e6d',
    b'221e6e',
    b'221e6f',
    b'221e70',
    b'221e44',
    b'221e71',
    b'221e72',
    b'221e73',
    b'221e74',
    b'221e75',
    b'221e76',
    b'221e77',
    b'221e78',
    b'221e79',
    b'221e7a',
    b'2 21e45',
    b'221e7b',
    b'221e7c',
    b'221e7d',
    b'221e7e',
    b'221e7f',
    b'221e80',
    b'221e81',
    b'221e82',
    b'221e83',
    b'221e84',
    b'221e46',
    b'221e85',
    b'221e86',
    b'221e87',
    b'221e88',
    b'221e89',
    b'221e8a',
    b'221e8b',
    b'221e8c',
    b'221e8d',
    b'221e8e',
    b'221e47',
    b'221e8F',
    b'221e90',
    b'221e91',
    b'221e92',
    b'221e93',
    b'221e94',
    b'221e95',
    b'221e96',
    b'221e97',
    b'221e98',
    b'221e48',
    b'221e99',
    b'221e9a',
    b'221e9b',
    b'221e9c',
    b'221e9d',
    b'221e9e',
    b'221e9f',
    b'221ea0',
    b'221ea1',
    b'221ea2',
    b'22189d',
    b'22189d',
    b'221e3d',
    b'221e0e',
    b'221e0f',
    b'220500',
    b'222a0b',
    b'221eae',
    b'221eb7',
    b'221eb8',
    b'221eb9',
    b'221eba',
    b'221ebb',
    b'221ebc',
    b'221ebd',
    b'227425',
    b'227426',
    b'221eaf',
    b'221eb0',
    b'221eb1',
    b'221eb2',
    b'221eb3',
    b'221eb4',
    b'221eb5',
    b'221eb6',
    b'221e32',
    b'221e32',
    b'221e3b',
    b'221620',
    b'22028c',
    b'22f40d',
]

CMDS2 = [
    b'22210e',
    b'220364',
    b'22295a',
    b'22f802',
]

class OdbcConn(object):

  def __init__(self):
    self.ser = serial.serial_for_url("/dev/rfcomm0", parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=1)
    self.keys = {}

  def GetKeys(self, init_cmd, commands):
    for i, cmd in enumerate(init_cmd):
      self._sendCommand(b'%s\r\n' % cmd)
    for cmd in commands:
      output = self._sendCommand(b'03%s55555555\r\n' % cmd)
      self.keys[cmd] = output
      print(cmd, output)

  def SaveDebugValues(self):
    with open('odb2_debug.log', 'a') as f:
      for key, v in self.keys.items():
        f.write('{0}, {1}\n'.format(key, v))

  def GetValues(self):
    values = {}

    for key, v in self.keys.items():
      if key == b'221E3B':
        b1 = int(v[8:10], 16)
        b2 = int(v[10:12], 16)
        values['DC_BATTERY_VOLTAGE'] = (b1 * pow(2, 8) + b2) / 4
      if key == b'221E3D':
        b1 = int(v[8:10], 16)
        b2 = int(v[10:12], 16)
        b3 = int(v[12:14], 16)
        b4 = int(v[14:16], 16)
    
        values['DC_BATTERY_CURRENT'] = ((b1 * pow(2, 32) + b2 * pow(2, 16) +
                                         b3 * pow(2, 8) + b4 - 150000) / 100) * -1
      if key == b'22028C':
        values['SOC_BMS'] = int(v[8:10],16) / 2.5
        values['SOC_DISPLAY'] = round(values['SOC_BMS'] * 51 / 46 - 6.4, 1)

      if key == b'22295A':
        b1 = int(v[8:10], 16)
        b2 = int(v[10:12], 16)
        b3 = int(v[12:14], 16)
        b4 = int(v[14:16], 16)
    
        values['ODO'] = (b1 * pow(2, 32) + b2 * pow(2, 16) + b3 * pow(2, 8) + b4) / 256

    return values

  def _sendCommand(self, msg):
    self.ser.flushInput()
    self.ser.write(msg)
    self.ser.flush()
    buffer = bytearray()
    while True:
      data = self.ser.read(self.ser.in_waiting or 1)
      if not data:
        break
      buffer.extend(data)
      if b'>' in buffer or b'OK' in buffer:
        break
    buffer = re.sub(b"\x00", b"", buffer)
    if buffer.endswith(b'>'):
      buffer = buffer[:-1]
    string = buffer.decode("utf-8", "ignore")
    lines = [s.strip() for s in re.split("[\r\n]", string) if bool(s)]
 
    return lines[1].replace(' ', '')


def main():
  success = False
  odbc_conn = OdbcConn()
  odbc_conn.GetKeys(INIT_CMD, CMDS)
  odbc_conn.GetKeys(INIT_CMD2, CMDS2)
  odbc_conn.GetKeys(INIT_CMD3, CMDS3)
  odbc_conn.GetKeys(INIT_CMD4, CMDS4)
  odbc_conn.GetKeys(INIT_CMD5, CMDS5)

  values = odbc_conn.GetValues()
  odbc_conn.SaveDebugValues()

  odbc_conn.ser.close()


if __name__ == '__main__':
  main()
