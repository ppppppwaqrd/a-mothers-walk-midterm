# Autoload — shared game state + checkpoint save
extends Node2D

var score: int = 0
## Sticky-rice baskets collected this run. Only kratib pickups count toward the happy ending.
var kratib: int = 0
var kratib_needed: int = 8
var hp: int = 100
var life: int = 4
var max_life: int = 5
var max_hp: int = 100

## Ai Tong patience / hunger (drains over time while playing a level).
var patience: float = 100.0
var max_patience: float = 100.0
## Visible within one level (~2 minutes full bar). Fail a thevada test to speed it up.
var patience_drain_per_sec: float = 0.9
## Raised when a rest-stop minigame is failed. Not saved; resets on a new level/run.
var patience_drain_mult: float = 1.0
var patience_active: bool = false
## Set when the run is already changing to a win/lose page.
var _ending: bool = false
## "patience" when Ai Tong's bar emptied; otherwise lives ran out.
var lose_reason: String = ""

## Mid-level shrine checkpoint (survives death within the same level).
var checkpoint_position: Vector2 = Vector2.ZERO
var has_level_checkpoint: bool = false

## Limited stone ammo.
var ammo: int = 5
var max_ammo: int = 10

var sfx_on: bool = true
var music_on: bool = true
## Bus levels, 0..1 linear, set from the pause menu sliders.
var music_volume: float = 0.8
var sfx_volume: float = 0.9
var fullscreen: bool = false

var player: Player = null
var current_level: String = "res://Scenes/Levels/level_01.tscn"
var save_path := "user://game.save"
var save_player_position: Vector2 = Vector2.ZERO

## Presentation cheat: fly, ignore damage, never run out of stones. Not saved.
var god_mode: bool = false
signal god_mode_changed(on: bool)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	call_deferred("_boot_settings")


func _boot_settings() -> void:
	load_option()
	apply_display()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("GodMode"):
		toggle_god_mode()
		get_viewport().set_input_as_handled()


func toggle_god_mode() -> void:
	god_mode = not god_mode
	if player != null and is_instance_valid(player) and player.has_method("apply_god_mode"):
		player.apply_god_mode(god_mode)
	god_mode_changed.emit(god_mode)
	AudioManager.play("ui_click")


func _process(delta: float) -> void:
	if _ending or get_tree().paused:
		return
	if not patience_active:
		return
	if player == null or not is_instance_valid(player):
		return
	if patience <= 0.0:
		end_from_patience()
		return
	patience = maxf(0.0, patience - patience_drain_per_sec * patience_drain_mult * delta)
	if patience <= 0.0:
		patience = 0.0
		end_from_patience()


func add_score(v: int = 1) -> void:
	score += v


func add_kratib(v: int = 1) -> void:
	kratib += v
	score += v


func has_happy_ending() -> bool:
	return kratib >= kratib_needed


func add_ammo(v: int = 3) -> void:
	ammo = mini(max_ammo, ammo + v)


func try_consume_ammo() -> bool:
	if god_mode:
		return true
	if ammo <= 0:
		return false
	ammo -= 1
	return true


func reset_run_resources() -> void:
	patience = max_patience
	patience_drain_mult = 1.0
	ammo = 5
	clear_level_checkpoint()


func fail_minigame() -> void:
	patience_drain_mult += 0.5


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
	kratib = 0
	hp = max_hp
	life = 4
	_ending = false
	lose_reason = ""
	reset_run_resources()
	save_player_position = Vector2.ZERO
	current_level = "res://Scenes/Levels/level_01.tscn"
	_clear_save()
	get_tree().change_scene_to_file("res://Scenes/Levels/story_intro.tscn")


func restart() -> void:
	new_game()


## Start the current level over from its beginning, keeping score and lives.
func retry_level() -> void:
	hp = max_hp
	_ending = false
	lose_reason = ""
	patience = max_patience
	patience_drain_mult = 1.0
	save_player_position = Vector2.ZERO
	clear_level_checkpoint()
	get_tree().change_scene_to_file(current_level)


## After Game Over: retry the last checkpoint level (not always level 1).
func retry_checkpoint() -> void:
	hp = max_hp
	life = 4
	_ending = false
	lose_reason = ""
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
	if level_path.begins_with("res://Scenes/Levels/menu") or level_path.begins_with("res://Scenes/Levels/credit") or level_path.begins_with("res://Scenes/Levels/options") or level_path.begins_with("res://Scenes/Levels/story_intro"):
		patience_active = false
		return
	# New level (not death reload) → clear mid-level shrine and thevada haste.
	if current_level != "" and current_level != level_path:
		clear_level_checkpoint()
		patience_drain_mult = 1.0
	current_level = level_path
	patience_active = true
	_ending = false
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
	if god_mode:
		return
	hp = hp - val
	if hp <= 0:
		death()


func add_hp(val: int = 1) -> void:
	hp = hp + val
	if hp > max_hp:
		hp = max_hp


func update_option() -> void:
	# The on/off toggles and the sliders both feed the same bus, so a muted
	# toggle wins regardless of where the slider sits.
	AudioManager.set_bus_volume(&"music", music_volume if music_on else 0.0)
	AudioManager.set_bus_volume(&"sfx", sfx_volume if sfx_on else 0.0)
	apply_display()


func apply_display() -> void:
	var mode := DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
	if DisplayServer.window_get_mode() != mode:
		DisplayServer.window_set_mode(mode)


func set_fullscreen(on: bool) -> void:
	fullscreen = on
	apply_display()
	save_option()


func add_life() -> void:
	if life < max_life:
		life += 1


func end_from_patience() -> void:
	if _ending:
		return
	_ending = true
	patience = 0.0
	patience_active = false
	lose_reason = "patience"
	if player != null and is_instance_valid(player):
		player.movement_enabled = false
	await get_tree().create_timer(0.4).timeout
	if not is_inside_tree():
		return
	clear_level_checkpoint()
	get_tree().change_scene_to_file("res://Scenes/Levels/game_over.tscn")


func death() -> void:
	if god_mode or _ending:
		return
	patience_active = false
	if player != null:
		await player.death_tween()
	life -= 1
	hp = max_hp
	patience = max_patience
	ammo = mini(max_ammo, maxi(ammo, 3))
	save_checkpoint()
	if life <= 0:
		lose_reason = "lives"
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
			"music_volume": music_volume,
			"sfx_volume": sfx_volume,
			"fullscreen": fullscreen,
			"lang": Locale.lang,
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
			music_volume = float(data.get("music_volume", music_volume))
			sfx_volume = float(data.get("sfx_volume", sfx_volume))
			fullscreen = bool(data.get("fullscreen", false))
			Locale.set_lang(str(data.get("lang", "th")), false)
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
		"kratib": kratib,
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
	# Levels all share base_level.tscn as their root, so ask the level for its id
	# instead of trusting scene_file_path.
	var scene := get_tree().current_scene
	if scene != null and scene.has_method("level_scene_path"):
		current_level = scene.level_scene_path()
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
	kratib = int(data.get("kratib", 0))
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
