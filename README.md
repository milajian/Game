# Python Tetris

A simple playable Tetris game built with Python and pygame.

## Features

- Classic 10x20 Tetris board
- 7 standard tetromino shapes
- Line clear, score, and level progression
- Next piece preview
- Keyboard controls for movement, rotation, soft drop, and hard drop

## Requirements

- Python 3.9+
- pygame

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python tetris.py
```

## Controls

- Left / Right Arrow: move piece
- Up Arrow: rotate piece
- Down Arrow: soft drop
- Space: hard drop

## Project Structure

- `tetris.py`: game source code
- `requirements.txt`: dependency list
- `.gitignore`: git ignore rules
