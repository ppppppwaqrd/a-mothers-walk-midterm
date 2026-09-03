class_name Player
extends CharacterBody2D

signal hit_enemy(enemy: Node2D)
signal hit_trap


# --------- VARIABLES ---------- #

@export_category("Player Properties")
@export var move_speed: float = 320
@export var jump_force: float = 720
@export var gravity: float = 28
@export var max_jump_count: int = 2
@export var bullet_scene: PackedScene
@export var shoot_cooldown_time: float = 0.2
@export var bullet_lifetime = 2.0

var jump_count: int = 2

@export_category("Toggle Functions")
@export var double_jump := false

var is_grounded: bool = false
var movement_enabled: bool = true
var spawn_point = Vector2(0, 0)
var is_attacking = false
var shoot_cooldown_timer = 0.0
var can_damage = true
var facing_right := true
var base_move_speed: float = 320.0
var base_jump_force: float = 720.0
var speed_boost_time: float = 0.0
var jump_boost_time: float = 0.0

## How long the landing crouch is held, and how fast the fall was that caused it.
const LAND_HOLD := 0.12
var _land_hold: float = 0.0
var _air_speed: float = 0.0

@onready var player_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var bullet_marker = $BulletMarker
@onready var particle_trails = $ParticleTrails
@onready var death_particles = $DeathParticles


# --------- BUILT-IN FUNCTIONS ---------- #
func _ready() -> void:
	base_move_speed = move_speed
	base_jump_force = jump_force
	spawn_point = global_position
	if GameManager.save_player_position.x != 0:
		global_position = GameManager.save_player_position
		GameManager.save_player_position = Vector2.ZERO
	player_sprite.play("Idle")
	apply_god_mode(GameManager.god_mode)


func apply_god_mode(on: bool) -> void:
	collision_mask = 0 if on else 1
	if has_node("Collision"):
		$Collision.monitoring = not on
	if not on:
		velocity.y = 0.0


func _physics_process(_delta):
	var was_airborne := not is_grounded
	is_grounded = is_on_floor()
	if was_airborne and is_grounded:
		_land(_air_speed)
	_air_speed = velocity.y if not is_grounded else 0.0
	movement()


func _process(_delta):
	_land_hold = maxf(0.0, _land_hold - _delta)
	_update_boosts(_delta)
	player_animations()
	flip_player()
	handle_shooting()
	_update_bullet_marker()
	if shoot_cooldown_timer > 0:
		shoot_cooldown_timer -= _delta


func _update_boosts(delta: float) -> void:
	if speed_boost_time > 0.0:
		speed_boost_time -= delta
		if speed_boost_time <= 0.0:
			move_speed = base_move_speed
	if jump_boost_time > 0.0:
		jump_boost_time -= delta
		if jump_boost_time <= 0.0:
			jump_force = base_jump_force


func apply_speed_boost(multiplier: float = 1.5, duration: float = 5.0) -> void:
	move_speed = base_move_speed * multiplier
	speed_boost_time = duration


func apply_jump_boost(multiplier: float = 1.35, duration: float = 5.0) -> void:
	jump_force = base_jump_force * multiplier
	jump_boost_time = duration


# --------- CUSTOM FUNCTIONS ---------- #

func movement():
	if GameManager.god_mode:
		_fly_movement()
		return
	if !is_on_floor():
		velocity.y += gravity
	elif is_on_floor():
		jump_count = max_jump_count
		velocity.x = 0

	handle_jumping()

	if movement_enabled:
		if Input.is_action_pressed("Left"):
			velocity.x = -move_speed
		if Input.is_action_pressed("Right"):
			velocity.x = move_speed
	if velocity.y > 5000:
		hit_trap.emit()
	move_and_slide()


func _fly_movement() -> void:
	velocity = Vector2.ZERO
	if not movement_enabled:
		move_and_slide()
		return
	if Input.is_action_pressed("Left"):
		velocity.x = -move_speed
	if Input.is_action_pressed("Right"):
		velocity.x = move_speed
	if Input.is_action_pressed("Jump"):
		velocity.y = -move_speed
	if Input.is_action_pressed("Down"):
		velocity.y = move_speed
	move_and_slide()


func handle_jumping():
	if Input.is_action_just_pressed("Jump") and movement_enabled:
		if is_on_floor() and !double_jump:
			jump()
		elif double_jump and jump_count > 0:
			jump()
			jump_count -= 1


func jump():
	jump_tween()
	AudioManager.play_varied("jump")
	velocity.y = -jump_force


func player_animations():
	particle_trails.emitting = false
	if is_attacking:
		return

	if is_on_floor():
		if _land_hold > 0.0:
			_play_anim("Land")
		elif abs(velocity.x) > 0:
			particle_trails.emitting = true
			_play_anim("Walk")
		else:
			_play_anim("Idle")
	else:
		_play_anim("Jump" if velocity.y < 0.0 else "Fall")


func _play_anim(anim_name: StringName) -> void:
	if player_sprite.animation != anim_name or not player_sprite.is_playing():
		player_sprite.play(anim_name)


func flip_player():
	if velocity.x < 0:
		facing_right = false
		player_sprite.flip_h = true
	elif velocity.x > 0:
		facing_right = true
		player_sprite.flip_h = false


func _update_bullet_marker() -> void:
	bullet_marker.position.x = 36.0 if facing_right else -36.0


func death_tween():
	AudioManager.play("death")
	death_particles.emitting = true
	movement_enabled = false
	var tween = create_tween()
	tween.tween_property(self, "scale", Vector2.ZERO, 0.15)
	tween.parallel().tween_property(self, "position", Vector2(position.x, position.y - 100), 0.15)
	await tween.finished
	global_position = spawn_point
	await get_tree().create_timer(0.3).timeout
	movement_enabled = true
	AudioManager.play("respawn")
	respawn_tween()


func respawn_tween():
	var tween = create_tween()
	tween.stop()
	tween.play()
	tween.tween_property(self, "scale", Vector2.ONE, 0.15)
	tween.parallel().tween_property(self, "position", spawn_point, 0.15)


func jump_tween():
	var tween = create_tween()
	tween.tween_property(self, "scale", Vector2(0.7, 1.4), 0.1)
	tween.tween_property(self, "scale", Vector2(1.0, 1.0), 0.1)


## Touchdown: hold the crouch drawing, squash, and kick up dust. Weight scales
## with the drop, so a step down barely registers and a long fall thumps.
func _land(fall_speed: float) -> void:
	var weight: float = clampf(fall_speed / 900.0, 0.0, 1.0)
	if weight < 0.12:
		return
	_land_hold = LAND_HOLD * weight
	particle_trails.emitting = true
	AudioManager.play_varied("land", -8.0 + 6.0 * weight)
	var tween := create_tween()
	tween.tween_property(self, "scale", Vector2(1.0 + 0.22 * weight, 1.0 - 0.22 * weight), 0.06)
	tween.tween_property(self, "scale", Vector2.ONE, 0.14).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)


func damage_tween():
	can_damage = false
	var squash := create_tween()
	squash.tween_property(self, "scale", Vector2(1.18, 0.82), 0.06)
	squash.tween_property(self, "scale", Vector2.ONE, 0.14).set_trans(Tween.TRANS_BACK)
	var tween = create_tween()
	for i in range(1, 6):
		tween.tween_property(player_sprite, "modulate", Color(1.0, 0.45, 0.4, 1.0), 0.08)
		tween.tween_property(player_sprite, "modulate", Color.WHITE, 0.08)
	await tween.finished
	can_damage = true


func _on_collision_body_entered(body):
	if body.is_in_group("Traps"):
		hit_trap.emit()
	if !can_damage:
		return
	if body.is_in_group("Enemy"):
		var dx = body.position.x - position.x
		velocity.y = -400
		if dx > 0:
			velocity.x = -300
		else:
			velocity.x = 300
		damage_tween()
		hit_enemy.emit(body)


func handle_shooting():
	if Input.is_action_just_pressed("Shoot") and movement_enabled and shoot_cooldown_timer <= 0:
		if not GameManager.god_mode and GameManager.ammo <= 0:
			return
		shoot()


func shoot():
	if bullet_scene == null:
		return
	if not GameManager.try_consume_ammo():
		return
	is_attacking = true
	player_sprite.play("Attack")
	var bullet = bullet_scene.instantiate()
	bullet.global_position = bullet_marker.global_position
	var angle = deg_to_rad(randf_range(0, 20))
	var sign_x = 1.0 if facing_right else -1.0
	var dir = Vector2(cos(angle) * sign_x, -sin(angle))
	get_parent().add_child(bullet)
	bullet.shoot(dir, 650, bullet_lifetime)
	AudioManager.play_varied("throw_stone")
	shoot_cooldown_timer = shoot_cooldown_time


func _on_animation_finished() -> void:
	if player_sprite.animation == &"Attack":
		is_attacking = false
