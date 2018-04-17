#!/usr/bin/env python3
'''
CPSC 415 -- Homework #3 support file
Stephen Davies, University of Mary Washington, fall 2017
'''

# Long long ago, I used chapter 4 of Chaudhary's "Tkinter GUI Blueprints" as a
# starting point for this. It has since evolved unrecognizeably.

import tkinter as tk
import sys
from pathlib import Path
import logging
import builtins

import chess_config

if len(sys.argv) > 4:
    print("Usage: main_chess.py [debugLevel] [configFile] [crazy=false].")
    sys.exit(1)

if len(sys.argv) > 1:
    logging.getLogger().setLevel(sys.argv[1])
else:
    logging.getLogger().setLevel('DEBUG')

if len(sys.argv) > 3:
    crazy = (sys.argv[3][sys.argv[3].index('=')+1:] if '=' in sys.argv[3]
        else sys.argv[3])
    crazy = crazy.lower() == 'true'
else:
    crazy = False

config_file_basename = sys.argv[2] if len(sys.argv) > 2 else 'reg'

builtins.cfg = chess_config.Config(config_file_basename, crazy)

import chess_view

root = tk.Tk()
chess_view.View(root)
root.mainloop()
