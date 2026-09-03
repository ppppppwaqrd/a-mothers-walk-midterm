class_name Enemy
extends CharacterBody2D

@export var speed = 100.0
@export var direction = 1
## Art sheets face right (boar/snake/crow). Set false for old left-facing mushrooms.
@export var sprite_faces_right: bool = true
## Hits from stones required to defeat this enemy.
@export var max_hits: int = 1
## How touching the player hurts them.
@export_enum("normal", "half_hp", "instant_kill") var touch_effect: String = "normal"
@export var touch_damage: int = 8

var alive = true
var hits_left: int = 1
var _turn_cool: float = 0.0
@onready var wall_ray: RayCast2D = $Sprite/Ray/wallRay
@onready var player_ray: RayCast2D = $Sprite/Ray/playerRay
@onready var floor_ray: RayCast2D = $Sprite/Ray/floorRay


func _ready() -> void:
	hits_left = maxi(1, max_hits)
	$DeathParticles.one_shot = true
	floor_block_on_wall = false
	floor_snap_length = 12.0
	for ray in [wall_ray, player_ray, floor_ray]:
		ray.add_exception(self)
		ray.collide_with_areas = false
		ray.hit_from_inside = false
	if direction > 0:
		direction = 1
	elif direction < 0:
		direction = -1
	_update_facing()


func get_touch_damage() -> int:
	match touch_effect:
		"instant_kill":
			return maxi(GameManager.hp, GameManager.max_hp)
		"half_hp":
			return maxi(1, int(ceili(float(GameManager.hp) * 0.5)))
		_:
			return touch_damage


func _physics_process(delta: float) -> void:
	_turn_cool = maxf(0.0, _turn_cool - delta)
	if not is_on_floor():
		velocity += get_gravity() * delta

	if alive and is_on_floor():
		if player_ray.is_colliding():
			found_player()
		elif _turn_cool <= 0.0 and (wall_ray.is_colliding() or not floor_ray.is_colliding()):
			direction = -direction
			_turn_cool = 0.45
			_update_facing()
		velocity.x = speed * direction
	else:
		velocity.x = 0

	move_and_slide()


func _update_facing() -> void:
	# Keep rays on the Sprite root (unscaled); aim them in move direction.
	var facing: int = 1 if direction > 0 else -1
	player_ray.target_position = Vector2(56.0 * facing, 0.0)
	wall_ray.target_position = Vector2(36.0 * facing, 0.0)
	floor_ray.position = Vector2(34.0 * facing, -10.0)

	var anim: AnimatedSprite2D = null
	if $Sprite.has_node("AnimateSprite"):
		anim = $Sprite.get_node("AnimateSprite") as AnimatedSprite2D
	if anim != null:
		# Right-facing art: flip when moving left. Left-facing art: opposite.
		anim.flip_h = (facing < 0) if sprite_faces_right else (facing > 0)
		$Sprite.scale.x = 1.0
	else:
		$Sprite.scale.x = -1.0 if ((facing < 0) == sprite_faces_right) else 1.0


func found_player() -> void:
	var point: Vector2 = player_ray.get_collision_point()
	var new_dir: int = -1 if position.x > point.x else 1
	if new_dir != direction and _turn_cool <= 0.0:
		direction = new_dir
		_turn_cool = 0.25
		_update_facing()


func _on_hit_area_body_entered(body: Node2D) -> void:
	if alive and body.is_in_group("Traps"):
		death_tween()
	if alive and body.is_in_group("Bullet"):
		hits_left -= 1
		body.queue_free()
		AudioManager.play_varied("stone_hit")
		if hits_left <= 0:
			GameManager.add_score()
			death_tween()
		else:
			_hit_flash()


## Take the hit visibly: flinch back from the stone, squash, and flash red. A
## multi-hit enemy needs this to read, or the player cannot tell it connected.
func _hit_flash() -> void:
	AudioManager.play_varied("enemy_hit")
	var target: CanvasItem = _art()
	var tween := create_tween()
	tween.tween_property(target, "modulate", Color(1, 0.4, 0.4, 1), 0.05)
	tween.tween_property(target, "modulate", Color(1, 1, 1, 1), 0.12)
	# Left-facing art is mirrored by a negative scale.x, so squash relative to
	# the sign it already carries instead of forcing it positive.
	var facing_scale: float = signf($Sprite.scale.x)
	var knock := create_tween().set_parallel(true)
	knock.tween_property($Sprite, "scale", Vector2(0.86 * facing_scale, 1.14), 0.06)
	knock.tween_property($Sprite, "position:x", -14.0 * direction, 0.06)
	knock.chain().tween_property($Sprite, "scale", Vector2(facing_scale, 1.0), 0.16).set_trans(Tween.TRANS_BACK)
	knock.parallel().tween_property($Sprite, "position:x", 0.0, 0.16)


## Go down rather than vanish: topple over, drift, and fade with the burst.
func death_tween() -> void:
	alive = false
	collision_layer = 0
	$DeathParticles.emitting = true
	AudioManager.play("enemy_death")
	var art := _art()
	if art is AnimatedSprite2D:
		art.pause()
	var fall := create_tween().set_parallel(true)
	fall.tween_property($Sprite, "rotation_degrees", 82.0 * -direction, 0.34).set_trans(Tween.TRANS_BACK)
	fall.tween_property($Sprite, "position:y", 12.0, 0.34)
	fall.tween_property(art, "modulate", Color(1, 1, 1, 0), 0.5).set_delay(0.22)
	await get_tree().create_timer(1).timeout
	queue_free()


## The AnimatedSprite2D if the enemy has one, else the Sprite root.
func _art() -> CanvasItem:
	if $Sprite.has_node("AnimateSprite"):
		return $Sprite.get_node("AnimateSprite") as CanvasItem
	return $Sprite
