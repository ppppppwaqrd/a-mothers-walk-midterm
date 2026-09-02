# Autoload — shared game state + checkpoint save
extends Node2D

var score: int = 0
var hp: int = 100
var life: int = 4
var max_life: int = 5
var max_hp: int = 100

## Ai Tong patience / hunger (drains over time while playing a level).
var patience: float = 100.0
var max_patience: float = 100.0
## ~5+ minutes for 6 levels (100 / 320 ≈ 0.31 per sec).
var patience_drain_per_sec: float = 0.31
var patience_active: bool = false

## Mid-level shrine checkpoint (survives death within the same level).
var checkpoint_position: Vector2 = Vector2.ZERO
var has_level_checkpoint: bool = false

## Limited stone ammo.
var ammo: int = 5
var max_ammo: int = 10

var sfx_on: bool = true
var music_on: bool = true

var player: Player = null
var current_level: String = "res://Scenes/Levels/level_01.tscn"
var save_path := "user://game.save"
var save_player_position: Vector2 = Vector2.ZERO


func _process(delta: float) -> void:
	if not patience_active:
		return
	if player == null or not is_instance_valid(player):
		return
	if patience <= 0.0:
		return
	patience = maxf(0.0, patience - patience_drain_per_sec * delta)
	if patience <= 0.0:
		patience = 0.0
		# Ai Tong ran out of patience — mother fails this attempt.
		death()


func add_score(v: int = 1) -> void:
	score += v


func add_ammo(v: int = 3) -> void:
	ammo = mini(max_ammo, ammo + v)


func try_consume_ammo() -> bool:
	if ammo <= 0:
		return false
	ammo -= 1
	return true


func reset_run_resources() -> void:
	patience = max_patience
	ammo = 5
	clear_level_checkpoint()


func clear_level_checkpoint() -> void:
	checkpoint_position = Vector2.ZERO
	has_level_checkpoint = false


func register_checkpoint(pos: Vector2) -> void:
	checkpoint_position = pos
	has_level_checkpoint = true
	if player != null and is_instance_valid(player):
		player.spawn_point = pos
	save_checkpoint()


func load_next_level(next_scene: PackedScene) -> void:
	clear_level_checkpoint()
	get_tree().change_scene_to_packed(next_scene)


func new_game() -> void:
	score = 0
	hp = max_hp
	life = 4
	reset_run_resources()
	save_player_position = Vector2.ZERO
	current_level = "res://Scenes/Levels/level_01.tscn"
	_clear_save()
	get_tree().change_scene_to_file(current_level)


func restart() -> void:
	new_game()


## After Game Over: retry the last checkpoint level (not always level 1).
func retry_checkpoint() -> void:
	hp = max_hp
	life = 4
	reset_run_resources()
	save_player_position = Vector2.ZERO
	if current_level == "" or not ResourceLoader.exists(current_level):
		current_level = "res://Scenes/Levels/level_01.tscn"
	save_checkpoint()
	get_tree().change_scene_to_file(current_level)


## Called by each level when it starts.
func on_level_entered(level_path: String) -> void:
	if level_path == "" or level_path.begins_with("res://Scenes/Levels/game_"):
		patience_active = false
		return
	if level_path.begins_with("res://Scenes/Levels/menu") or level_path.begins_with("res://Scenes/Levels/credit") or level_path.begins_with("res://Scenes/Levels/options"):
		patience_active = false
		return
	# New level (not death reload) → clear mid-level shrine.
	if current_level != "" and current_level != level_path:
		clear_level_checkpoint()
	current_level = level_path
	patience_active = true
	save_checkpoint()
	if player != null:
		if has_level_checkpoint and checkpoint_position != Vector2.ZERO:
			player.global_position = checkpoint_position
			player.spawn_point = checkpoint_position
		elif save_player_position != Vector2.ZERO:
			player.global_position = save_player_position
			player.spawn_point = save_player_position
			save_player_position = Vector2.ZERO


func damage(val: int = 1) -> void:
	hp = hp - val
	if hp <= 0:
		death()


func add_hp(val: int = 1) -> void:
	hp = hp + val
	if hp > max_hp:
		hp = max_hp


func update_option() -> void:
	var music_bus := AudioServer.get_bus_index("music")
	var sfx_bus := AudioServer.get_bus_index("sfx")
	AudioServer.set_bus_mute(sfx_bus, not sfx_on)
	AudioServer.set_bus_mute(music_bus, not music_on)


func add_life() -> void:
	if life < max_life:
		life += 1


func death() -> void:
	patience_active = false
	if player != null:
		await player.death_tween()
	life -= 1
	hp = max_hp
	patience = max_patience
	ammo = mini(max_ammo, maxi(ammo, 3))
	save_checkpoint()
	if life <= 0:
		clear_level_checkpoint()
		get_tree().change_scene_to_file("res://Scenes/Levels/game_over.tscn")
	else:
		# Respawn same level at shrine checkpoint if set.
		save_player_position = Vector2.ZERO
		get_tree().change_scene_to_file(current_level)


func save_option() -> void:
	var file := FileAccess.open("user://option.json", FileAccess.WRITE)
	if file:
		var payload: Dictionary = {
			"music": music_on,
			"sound": sfx_on,
		}
		file.store_pascal_string(JSON.stringify(payload, "  "))
		file.close()


func load_option() -> void:
	if FileAccess.file_exists("user://option.json"):
		var file := FileAccess.open("user://option.json", FileAccess.READ)
		var text: String = file.get_pascal_string()
		var data = JSON.parse_string(text)
		file.close()
		if typeof(data) == TYPE_DICTIONARY:
			music_on = data.get("music", true)
			sfx_on = data.get("sound", true)
			update_option()


func save_checkpoint() -> void:
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		return
	var pos: Array = [0.0, 0.0]
	if player != null:
		pos = [player.global_position.x, player.global_position.y]
	var payload: Dictionary = {
		"current_level": current_level,
		"player": pos,
		"score": score,
		"life": life,
		"hp": hp,
		"patience": patience,
		"ammo": ammo,
		"has_level_checkpoint": has_level_checkpoint,
		"checkpoint": [checkpoint_position.x, checkpoint_position.y],
	}
	file.store_pascal_string(JSON.stringify(payload, "  "))
	file.close()


func save_game() -> void:
	var scene := get_tree().current_scene
	if scene != null and scene.scene_file_path != "":
		current_level = scene.scene_file_path
	save_checkpoint()


func has_gamesaved() -> bool:
	return FileAccess.file_exists(save_path)


func load_game() -> void:
	if not FileAccess.file_exists(save_path):
		new_game()
		return
	var file := FileAccess.open(save_path, FileAccess.READ)
	var text: String = file.get_pascal_string()
	var data = JSON.parse_string(text)
	file.close()
	if typeof(data) != TYPE_DICTIONARY:
		new_game()
		return
	current_level = str(data.get("current_level", current_level))
	score = int(data.get("score", score))
	life = int(data.get("life", 4))
	hp = int(data.get("hp", max_hp))
	patience = float(data.get("patience", max_patience))
	ammo = int(data.get("ammo", 5))
	has_level_checkpoint = bool(data.get("has_level_checkpoint", false))
	var cp = data.get("checkpoint", [0, 0])
	if typeof(cp) == TYPE_ARRAY and cp.size() >= 2:
		checkpoint_position = Vector2(float(cp[0]), float(cp[1]))
	else:
		checkpoint_position = Vector2.ZERO
	var pos = data.get("player", [0, 0])
	if typeof(pos) == TYPE_ARRAY and pos.size() >= 2:
		save_player_position = Vector2(float(pos[0]), float(pos[1]))
	else:
		save_player_position = Vector2.ZERO
	if life <= 0:
		life = 4
		hp = max_hp
		reset_run_resources()
	get_tree().change_scene_to_file(current_level)


func _clear_save() -> void:
	if FileAccess.file_exists(save_path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path))
