extends CharacterBody2D

# This script provides simple AI for an opponent character.

@export var speed: float = 150.0
@export var health: float = 100.0
@export var player_node: Node2D = null # Assign the player node in the editor.

@onready var character_loader: Sprite2D = $CharacterLoader
var hurtbox: Area2D
var fight_ui: CanvasLayer

enum State { IDLE, CHASING, ATTACKING }
var current_state: State = State.IDLE

var decision_timer: Timer

const ATTACK_RANGE = 100.0 # The distance at which the AI will try to attack.
const SIGHT_RANGE = 800.0  # The distance at which the AI will notice the player.

func _ready():
	# Find the FightUI node in the scene.
	fight_ui = get_tree().get_root().find_child("FightUI", true, false)

	# Create a hurtbox for the character.
	hurtbox = Area2D.new()
	hurtbox.name = "Hurtbox"
	hurtbox.collision_layer = 0
	hurtbox.collision_mask = 1 # Scan for hitboxes on layer 1
	add_child(hurtbox)

	# The shape of the hurtbox.
	var hurtbox_shape = CollisionShape2D.new()
	var rectangle = RectangleShape2D.new()
	rectangle.size = Vector2(80, 180)
	hurtbox_shape.shape = rectangle
	hurtbox.add_child(hurtbox_shape)

	hurtbox.area_entered.connect(self._on_hurtbox_area_entered)

	# Timer to make decisions every so often.
	decision_timer = Timer.new()
	decision_timer.wait_time = 0.5 # Make a decision every half a second.
	decision_timer.one_shot = false
	decision_timer.timeout.connect(self._make_decision)
	add_child(decision_timer)
	decision_timer.start()

func _physics_process(delta):
	match current_state:
		State.IDLE:
			velocity.x = move_toward(velocity.x, 0, speed)
			character_loader.play_animation("idle")
		State.CHASING:
			if player_node:
				var direction = (player_node.global_position - global_position).normalized()
				velocity.x = direction.x * speed
				character_loader.play_animation("walk")
			else:
				# No player, so go back to idle.
				current_state = State.IDLE
		State.ATTACKING:
			velocity.x = 0
			# In a real game, you'd have a cooldown for attacks.
			# For simplicity, we just play the animation once per decision.

	move_and_slide()

	# Flip the sprite based on the direction of movement.
	if velocity.x != 0:
		character_loader.scale.x = sign(velocity.x)

func _make_decision():
	if not player_node:
		current_state = State.IDLE
		return

	var distance_to_player = global_position.distance_to(player_node.global_position)

	if distance_to_player <= ATTACK_RANGE:
		current_state = State.ATTACKING
		_perform_attack()
	elif distance_to_player <= SIGHT_RANGE:
		current_state = State.CHASING
	else:
		current_state = State.IDLE

func _perform_attack():
	# Randomly choose between punch and kick.
	if randf() > 0.5:
		character_loader.play_animation("punch")
	else:
		character_loader.play_animation("kick")

func take_damage(amount: float):
	health -= amount
	if health < 0:
		health = 0
	print("AI took ", amount, " damage, health is now ", health)

	if fight_ui:
		fight_ui.set_health("player2", health)

	if health == 0:
		# Handle death
		print("AI has been defeated!")
		set_physics_process(false) # Disable further processing
		decision_timer.stop()

func _on_hurtbox_area_entered(area: Area2D):
	# The area that entered is a hitbox.
	if area.has_meta("damage"):
		var damage = area.get_meta("damage", 0)
		take_damage(damage)
		# To prevent multiple hits from a single attack, disable the hitbox.
		area.queue_free()
