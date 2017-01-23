# (Hey Scotty, how can I set the 'include' path for python ?)
import os, sys, inspect
# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
cmd_folder +=  '/../api/python'
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import flaschen

UDP_IP = 'ft.noise'
UDP_PORT = 1337
ft = flaschen.Flaschen(UDP_IP, UDP_PORT, 45, 35, 5)


"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def print_volume_handler(unused_addr, args, volume):
    if volume > 1.0:
        volume = 1.0
    if volume < 0.0:
        volume = 0.0
    translated_volume = int(translate(volume, 0, 1, 0, 255))
    print("[{0}] ~ ORIG:{2} MAPPED_TO:{1}".format(args[0], translated_volume, volume))
    for y in range(0, ft.height):
      for x in range(0, ft.width):
        ft.set(x, y, (translated_volume, 0, 0))
    ft.send()

def decibel_vol_handler(unused_addr, args, volume):
    # if volume > 0.0:
    #     volume = 0.0
    # if volume < -120.0:
    #     volume = -120.0
    translated_volume = int(translate(volume, 120, 0, 0, 255))
    print("decibel [{0}] ~ ORIG:{2} MAPPED_TO:{1}".format(args[0], translated_volume, volume))
    for y in range(0, ft.height):
      for x in range(0, ft.width):
        ft.set(x, y, (translated_volume, 0, 0))
    ft.send()

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    # dispatcher.map("/filter", print)
    dispatcher.map("/volume", decibel_vol_handler, "Volume")
    dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

    server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
