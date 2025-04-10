import PySimpleGUI as sg
import json
import random
from datetime import datetime



class PlayerRepository:
    """Handles loading and saving player data."""

    def __init__(self, filename: str):
        """Initialize the repository with a data file.

        Args:
            filename: Name of the file to store player data
        """
        self.filename = filename
        self.players = self._load_players()

    def _load_players(self) -> dict[str, float]:
        """Load players from file.

        Returns:
            Dictionary of player names and their ratings
        """
        try:
            with open(self.filename) as f:
                return json.loads(f.read())
        except FileNotFoundError:
            print(f"Player data file '{self.filename}' not found. Starting with empty data.")
            return {}

    def save_players(self, timestamp: bool = True) -> None:
        """Save players to file.

        Args:
            timestamp: Whether to add a timestamp to the filename
        """
        filename = self.filename
        if timestamp:
            filename = f"{self.filename}_{datetime.now().strftime('%H.%M.%S_%d.%m')}"

        try:
            with open(filename, 'w') as file:
                json.dump(self.players, file)
        except Exception as e:
            print(f"Error saving player data: {str(e)}")

    def update_player_rating(self, player_name: str, points: float) -> None:
        """Update a player's rating.

        Args:
            player_name: Name of the player to update
            points: Points to add (positive) or subtract (negative)
        """
        if player_name in self.players:
            self.players[player_name] += points

    def get_player_list(self) -> list[str]:
        """Get sorted list of player names.

        Returns:
            Alphabetically sorted list of player names
        """
        return sorted(list(self.players.keys()))

class TeamBalancer:
    """Handles team balancing logic."""

    def __init__(self, player_repository: PlayerRepository):
        """Initialize with player repository.

        Args:
            player_repository: Repository containing player data
        """
        self.player_repository = player_repository
        self.maps = [
            "Huta w Essen", "Hill 400", "La Gleize", "Stepy", "Miasto 17",
            "Generał Błoto", "Redball", "Whiteball", "Las Lienne",
            "Atak na Lorch", "Nordwind", "Port w Hamburgu", "Road to Arnhem"
        ]
        # Point calculation constants
        self.points_constant = 0.2
        self.points_per_500 = 0.2
        self.diff_amortization = 0.1
        self.min_gained_points = 0.1

        # Current teams
        self.team1 = {}
        self.team2 = {}
        self.team_diff = 0.0

    def generate_teams(self, selected_players: list[str]) -> tuple[dict[str, float], dict[str, float], float]:
        """Generate balanced teams from selected players.

        Args:
            selected_players: List of player names to balance

        Returns:
            Tuple containing (team1, team2, point_difference)
        """
        player_ratings = {}
        for player in selected_players:
            if player in self.player_repository.players:
                player_ratings[player] = self.player_repository.players[player]

        self.team1, self.team2, self.team_diff = self._find_closest_combination(player_ratings)
        return self.team1, self.team2, self.team_diff

    @staticmethod
    def _find_closest_combination(players: dict[str, float]) -> tuple[dict[str, float], dict[str, float], float]:
        """Find the most balanced team combination.

        Args:
            players: Dictionary of player names and ratings

        Returns:
            Tuple containing (team1, team2, point_difference)
        """
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        team1, team2 = {}, {}
        sum1, sum2 = 0, 0

        for player, score in sorted_players:
            if len(team1) < len(team2):
                team1[player] = score
                sum1 += score
            elif len(team2) < len(team1):
                team2[player] = score
                sum2 += score
            else:
                if sum1 <= sum2:
                    team1[player] = score
                    sum1 += score
                else:
                    team2[player] = score
                    sum2 += score

        diff = abs(sum1 - sum2)
        return team1, team2, diff

    def select_random_map(self) -> str:
        return random.choice(self.maps)

    @staticmethod
    def assign_random_sides() -> bool:
        """Randomly assign Allies/Axis to teams.

        Returns:
            True if Team 1 is Axis, False if Team 1 is Allies
        """
        return random.randrange(2) == 0  # True = Team 1 Axis, False = Team 1 Allies

    def update_match_results(self, winning_team: int, points_scored: int) -> None:
        """Update player ratings based on match results.

        Args:
            winning_team: Team number that won (1 or 2)
            points_scored: Number of points scored by winning team
        """
        # Calculate team sums
        sum1 = sum(self.team1.values())
        sum2 = sum(self.team2.values())
        team_diff = sum1 - sum2

        # Calculate rating quotient (for normalization)
        all_ratings = list(self.player_repository.players.values())
        if all_ratings and max(all_ratings) > 0:
            quotient = min(all_ratings) / max(all_ratings)
        else:
            quotient = 1.0

        # Adjust team_diff based on which team was favored
        if (team_diff > 0 and winning_team == 1) or (team_diff < 0 and winning_team == 2):
            # Favored team won
            adjusted_diff = -abs(team_diff)
        else:
            # Underdog team won
            adjusted_diff = abs(team_diff)

        # Update ratings for both teams
        if winning_team == 1:
            self._update_team_ratings(self.team1, adjusted_diff, True, points_scored, quotient)
            self._update_team_ratings(self.team2, adjusted_diff, False, points_scored, quotient)
        else:
            self._update_team_ratings(self.team2, adjusted_diff, True, points_scored, quotient)
            self._update_team_ratings(self.team1, adjusted_diff, False, points_scored, quotient)

        # Save updated ratings
        self.player_repository.save_players()

    def _update_team_ratings(self, team: dict[str, float], diff: float, won: bool,
                             points_scored: int, quotient: float) -> None:
        """Update ratings for players in a team.

        Args:
            team: Dictionary of players and their ratings
            diff: Team skill difference
            won: Whether the team won
            points_scored: Points scored by winning team
            quotient: Rating normalization factor
        """
        for player in team:
            points = self._calculate_points(diff, won, points_scored, quotient)
            self.player_repository.update_player_rating(player, points)

    def _calculate_points(self, diff: float, won: bool, points_scored: int, quotient: float) -> float:
        """Calculate rating points to add/subtract.

        Args:
            diff: Team skill difference
            won: Whether the team won
            points_scored: Points scored by winning team
            quotient: Rating normalization factor

        Returns:
            Points to add or subtract from player rating
        """
        base_points = (
                              self.points_constant +
                              self.points_per_500 * (points_scored / 500) +
                              self.diff_amortization * diff
                      ) * quotient

        if not won:
            base_points = -base_points

        # Ensure minimum point change
        if won:
            return max(base_points, self.min_gained_points)
        else:
            return min(base_points, -self.min_gained_points)


class BalancerGUI:
    """GUI for the team balancer application."""

    def __init__(self, balancer: TeamBalancer, player_repository: PlayerRepository):
        """Initialize the GUI.

        Args:
            balancer: TeamBalancer instance
            player_repository: PlayerRepository instance
        """
        self.balancer = balancer
        self.player_repository = player_repository
        self.window = None
        self.combo_keys = [f"P{i}" for i in range(1, 9)]
        self._create_window()

    def _create_window(self) -> None:
        """Create the PySimpleGUI window."""
        player_names = self.player_repository.get_player_list()

        layout = [
            [sg.Text('Git gut or die trying')],
            [sg.Button('Refresh Players')],
            [
                sg.Combo(values=player_names, size=(12, 20), key="P1", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P2", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P3", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P4", enable_events=True, readonly=False)
            ],
            [
                sg.Combo(values=player_names, size=(12, 20), key="P5", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P6", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P7", enable_events=True, readonly=False),
                sg.Combo(values=player_names, size=(12, 20), key="P8", enable_events=True, readonly=False)
            ],
            [sg.Button('Generate Teams')],
            [sg.Text('Which team won?'), sg.Text(''), sg.Text('Winning team score')],
            [sg.Combo(['1', '2'], key="TeamPick"), sg.Text('                  '), sg.Input(size=(5, 2), key="Points")],
            [sg.Button('Confirm Results')],
            [sg.Output(size=(110, 20))]
        ]

        self.window = sg.Window('CoH2 Team Balancer', layout, finalize=True)

        # Bind key events for combo boxes
        for key in self.combo_keys:
            self.window[key].bind("<KeyRelease>", "KeyRelease")

    def run(self) -> None:
        """Run the GUI event loop."""
        while True:
            event, values = self.window.read(timeout=100)

            if event == sg.WIN_CLOSED:
                break

            elif event == 'Refresh Players':
                self.player_repository = PlayerRepository(self.player_repository.filename)
                player_names = self.player_repository.get_player_list()
                for key in self.combo_keys:
                    self.window[key].update(values=player_names)

            elif any(event == f"{key}KeyRelease" for key in self.combo_keys):
                key = event.replace("KeyRelease", "")
                input_text = values[key]
                player_names = self.player_repository.get_player_list()
                filtered_items = [
                    item for item in player_names
                    if input_text.lower() == item[0:len(input_text)].lower()
                ]
                self.window[key].update(values=filtered_items, value=input_text)

            elif event == 'Generate Teams':
                try:
                    selected_players = [values[key] for key in self.combo_keys if values[key]]
                    if len(selected_players) < 2:
                        print("Please select at least 2 players")
                        continue

                    team1, team2, diff = self.balancer.generate_teams(selected_players)

                    print("Team 1: ", {key: round(value, 2) for key, value in team1.items()})
                    print("Team 2: ", {key: round(value, 2) for key, value in team2.items()})
                    print(f"Difference: {diff:.2f}")

                    random_map = self.balancer.select_random_map()
                    print(f"\nMap: {random_map}\n")

                    is_team1_axis = self.balancer.assign_random_sides()
                    if is_team1_axis:
                        print("Team 1: Axis\nTeam 2: Allies")
                    else:
                        print("Team 1: Allies\nTeam 2: Axis")

                except Exception as e:
                    print(f"Error generating teams: {str(e)}")

            elif event == 'Confirm Results':
                try:
                    winning_team = int(values["TeamPick"])
                    points = int(values["Points"])

                    if winning_team not in [1, 2]:
                        print("Please select team 1 or 2 as the winner")
                        continue

                    self.balancer.update_match_results(winning_team, points)
                    print(f"\nTeam {winning_team} won and gained rating points\n")

                except ValueError:
                    print("Please enter valid numbers for team and points")
                except Exception as e:
                    print(f"Error updating results: {str(e)}")

        self.window.close()


def main():
    """Main application entry point."""
    # Configuration
    data_file = 'cohstats'

    # Initialize components
    player_repository = PlayerRepository(data_file)
    team_balancer = TeamBalancer(player_repository)
    gui = BalancerGUI(team_balancer, player_repository)

    # Run application
    gui.run()


if __name__ == "__main__":
    main()
