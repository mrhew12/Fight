extends CanvasLayer

# This script manages the fight UI, including health bars, timer, and round info.

# References to the UI nodes. These should be assigned in the Godot editor.
@onready var player1_health_bar: TextureProgressBar = $Player1HealthBar
@onready var player2_health_bar: TextureProgressBar = $Player2HealthBar
@onready var timer_label: Label = $TimerLabel
@onready var round_label: Label = $RoundLabel

var round_time_remaining: int = 99
var round_timer: Timer

func _ready():
	# Set up the round timer.
	round_timer = Timer.new()
	round_timer.wait_time = 1.0
	round_timer.one_shot = false
	round_timer.timeout.connect(self._on_round_timer_timeout)
	add_child(round_timer)
	round_timer.start()

	# Initialize the UI.
	update_timer_label()
	set_round(1)

	# Set initial health values.
	set_health("player1", 100)
	set_health("player2", 100)

func _on_round_timer_timeout():
	if round_time_remaining > 0:
		round_time_remaining -= 1
		update_timer_label()
	else:
		round_timer.stop()
		# Handle round end logic (e.g., emit a signal).
		print("Round over!")

func update_timer_label():
	timer_label.text = str(round_time_remaining)

# --- Public Methods ---

func set_health(player_id: String, health_percentage: float):
	"""
	Sets the health bar for a given player.
	player_id should be "player1" or "player2".
	health_percentage should be between 0 and 100.
	"""
	if player_id == "player1":
		player1_health_bar.value = health_percentage
	elif player_id == "player2":
		player2_health_bar.value = health_percentage
	else:
		print("Error: Invalid player ID for set_health.")

func set_round(round_number: int):
	"""
	Sets the round information text.
	"""
	round_label.text = "Round " + str(round_number)

func show_message(message: String, duration: float = 2.0):
	"""
	Shows a message in the center of the screen for a short duration.
	e.g., "Fight!", "K.O.!"
	"""
	var message_label = Label.new()
	message_label.text = message
	# In a real game, you would set the font, size, and position.
	# For now, we'll just add it as a child.
	add_child(message_label)

	# Timer to remove the message after the duration.
	var message_timer = Timer.new()
	message_timer.wait_time = duration
	message_timer.one_shot = true
	message_timer.timeout.connect(message_label.queue_free)
	add_child(message_timer)
	message_timer.start()
