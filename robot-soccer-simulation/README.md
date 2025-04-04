# Robot Soccer Simulation

This project is a simple robot soccer simulation built using Python and the Pygame library. It demonstrates basic object-oriented programming principles and includes features such as collision detection and a user interface for game settings.

## Project Structure

```
robot-soccer-simulation
├── src
│   ├── main.py                # Entry point of the simulation
│   ├── game                   # Contains game-related classes and logic
│   │   ├── __init__.py
│   │   ├── field.py           # Class for the soccer field
│   │   ├── robot.py           # Class for the robots
│   │   ├── ball.py            # Class for the soccer ball
│   │   └── collision.py        # Collision detection functions
│   ├── ui                     # Contains user interface components
│   │   ├── __init__.py
│   │   ├── menu.py            # Class for the game menu
│   │   └── scoreboard.py       # Class for displaying the score
│   └── utils                  # Utility functions and helpers
│       ├── __init__.py
│       └── helpers.py         # Helper functions
├── requirements.txt           # Project dependencies
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd robot-soccer-simulation
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the simulation:**
   Execute the main script:
   ```
   python src/main.py
   ```

## Usage

- Use the menu to start a new game or adjust settings.
- Control the robots using the designated keys (to be defined in the menu).
- The scoreboard will display the current score and game statistics.

## Contributing

Feel free to submit issues or pull requests for improvements and features. 

## License

This project is licensed under the MIT License. See the LICENSE file for details.