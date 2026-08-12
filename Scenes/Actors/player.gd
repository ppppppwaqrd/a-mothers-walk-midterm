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


func _physics_process(_delta):
	is_grounded = is_on_floor()
	movement()


func _process(_delta):
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


func handle_jumping():
	if Input.is_action_just_pressed("Jump") and movement_enabled:
		if is_on_floor() and !double_jump:
			jump()
		elif double_jump and jump_count > 0:
			jump()
			jump_count -= 1


func jump():
	jump_tween()
	AudioManager.jump_sfx.play()
	velocity.y = -jump_force


func player_animations():
	particle_trails.emitting = false
	if is_attacking:
		return

	if is_on_floor():
		if abs(velocity.x) > 0:
			particle_trails.emitting = true
			_play_anim("Walk")
		else:
			_play_anim("Idle")
	else:
		_play_anim("Jump")


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
	AudioManager.death_sfx.play()
	death_particles.emitting = true
	movement_enabled = false
	var tween = create_tween()
	tween.tween_property(self, "scale", Vector2.ZERO, 0.15)
	tween.parallel().tween_property(self, "position", Vector2(position.x, position.y - 100), 0.15)
	await tween.finished
	global_position = spawn_point
	await get_tree().create_timer(0.3).timeout
	movement_enabled = true
	AudioManager.respawn_sfx.play()
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


func damage_tween():
	var tween = create_tween()
	tween.stop()
	tween.play()
	can_damage = false
	for i in range(1, 10):
		tween.tween_property(player_sprite, "modulate", Color.RED, 0.1)
		tween.tween_property(player_sprite, "modulate", Color.WHITE, 0.1)
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
		if GameManager.ammo <= 0:
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
	if AudioManager.has_method("play_throw"):
		AudioManager.play_throw()
	shoot_cooldown_timer = shoot_cooldown_time


func _on_animation_finished() -> void:
	if player_sprite.animation == &"Attack":
		is_attacking = false
