extends CharacterBody2D

# This script controls the player character, handling input, movement, and health.

@export var speed: float = 200.0
@export var health: float = 100.0

# A reference to the character loader, which handles animations.
@onready var character_loader: Sprite2D = $CharacterLoader
var hurtbox: Area2D
var fight_ui: CanvasLayer

func _ready():
	# Find the FightUI node in the scene.
	fight_ui = get_tree().get_root().find_child("FightUI", true, false)

	# Create a hurtbox for the character.
	hurtbox = Area2D.new()
	hurtbox.name = "Hurtbox"
	hurtbox.collision_layer = 0
	hurtbox.collision_mask = 1 # Scan for hitboxes on layer 1
	add_child(hurtbox)

	# The shape of the hurtbox. For simplicity, we'll make it a static rectangle.
	var hurtbox_shape = CollisionShape2D.new()
	var rectangle = RectangleShape2D.new()
	rectangle.size = Vector2(80, 180) # A reasonable default size.
	hurtbox_shape.shape = rectangle
	hurtbox.add_child(hurtbox_shape)

	hurtbox.area_entered.connect(self._on_hurtbox_area_entered)

func _physics_process(delta):
	# Get input direction.
	var direction = Input.get_axis("ui_left", "ui_right")

	# Handle movement.
	if direction:
		velocity.x = direction * speed
		character_loader.play_animation("walk")
	else:
		velocity.x = move_toward(velocity.x, 0, speed)
		character_loader.play_animation("idle")

	# Handle actions.
	if Input.is_action_just_pressed("ui_accept"): # 'ui_accept' is usually spacebar or enter
		character_loader.play_animation("punch")
	elif Input.is_action_just_pressed("ui_select"): # 'ui_select' is usually enter
		character_loader.play_animation("kick")

	move_and_slide()

	# Flip the sprite based on the direction of movement.
	if velocity.x != 0:
		character_loader.scale.x = sign(velocity.x)

func take_damage(amount: float):
	health -= amount
	if health < 0:
		health = 0
	print("Player took ", amount, " damage, health is now ", health)

	if fight_ui:
		fight_ui.set_health("player1", health)

	if health == 0:
		# Handle death (e.g., play death animation, end round)
		print("Player has been defeated!")
		set_physics_process(false) # Disable further processing

func _on_hurtbox_area_entered(area: Area2D):
	# The area that entered is a hitbox.
	if area.has_meta("damage"):
		var damage = area.get_meta("damage", 0)
		take_damage(damage)
		# To prevent multiple hits from a single attack, disable the hitbox.
		area.queue_free()
