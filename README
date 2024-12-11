# Among Us IRL

This project is a simplified **Among Us**-inspired multiplayer game designed for real-life (IRL) gameplay. Built with Flask, it features role assignment, task completion, sabotage, and voting mechanics, all managed via a lightweight server-based environment.

---

## Features

- **Admin Panel**:
  - Login and manage games.
  - Configure game settings (e.g., number of tasks, impostor cooldown).
  - Reset and restart games easily.

- **Player Interaction**:
  - Join games via unique game IDs.
  - Crewmates complete tasks to win.
  - Impostor sabotages or eliminates crewmates to achieve victory.

- **Game Mechanics**:
  - Role assignment: Impostors and crewmates.
  - Voting system for emergency meetings and body reports.
  - Sabotage system with repair mechanics.
  - Win conditions based on completed tasks or elimination dynamics.

- **User Interface**:
  - Dynamic progress bars for task completion.
  - Real-time game state updates.
  - Light/Dark theme toggle for enhanced accessibility.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Flask

Install required Python packages:
```bash
pip install flask
```

### Running the Application

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/among-us-clone.git
   cd among-us-clone
   ```

2. Start the Flask server:
   ```bash
   python main.py
   ```

3. Open your browser and navigate to `http://localhost:8080`.

---

## Folder Structure

```
.
├── app.py                 # Main Flask application
├── templates/             # HTML templates for rendering pages
│   ├── admin_dashboard.html
│   ├── admin_game.html
│   ├── admin_login.html
│   ├── join_game.html
│   ├── player_game.html
├── static/                # Static files (CSS, JS, etc.)
│   ├── styles.css         # Custom styles
└── README.md              # Project documentation
```

---

## Key Routes

### Admin

| Route                     | Description                        |
|---------------------------|------------------------------------|
| `/admin/login`            | Admin login page                  |
| `/admin/dashboard`        | Create and manage games           |
| `/admin/game/<game_id>`   | View and control specific games    |

### Player

| Route                     | Description                        |
|---------------------------|------------------------------------|
| `/join`                   | Join a game using game ID         |
| `/game`                   | Player game view                  |
| `/complete_task`          | Complete assigned tasks           |
| `/report_body`            | Report a body                     |
| `/emergency_meeting`      | Call an emergency meeting         |

---

## Game Logic

1. **Setup**:
   - Admin creates a game and sets the number of tasks and impostor cooldown.
   - Players join using the unique game ID.

2. **Roles**:
   - Crewmates aim to complete all tasks or eject the impostor.
   - The impostor sabotages systems or eliminates crewmates to win.

3. **Tasks**:
   - Tasks are randomly assigned to crewmates.
   - Players report completed tasks to contribute to team progress.

4. **Voting**:
   - Triggered by emergency meetings or body reports.
   - Players vote to eject a suspected impostor or skip.

5. **Sabotage**:
   - Impostor triggers sabotage events.
   - Crewmates must repair sabotage to avoid losing.

6. **Win Conditions**:
   - **Crewmates win**: Complete all tasks or eject the impostor.
   - **Impostor wins**: Eliminate enough crewmates or achieve sabotage success.

---

## Playing IRL

This version is designed for players participating in the same physical space, where:

- Players use their devices to interact with the game interface (tasks, voting, sabotage).
- Movement, task zones, and physical "body reports" occur in the real-world setting.
- Admin serves as a referee to oversee the flow of the game and handle disputes.

**Example Gameplay Flow**:
1. Players join the game and receive their roles (Crewmate or Impostor) via the interface.
2. Crewmates physically move to task zones and use the app to "complete" tasks.
3. Impostors can stealthily "eliminate" crewmates and initiate sabotages through the app.
4. Players call emergency meetings or report bodies via their devices to discuss and vote.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests with improvements or new features.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Screenshots

Will appear soon

---

## Acknowledgments

Inspired by the popular game *Among Us*. This project is a simplified, non-commercial implementation for learning and demonstration purposes.