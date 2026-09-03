extends Node2D

## Which level this scene is, e.g. "level_03". Every level scene has this same
## base scene as its root, so `scene_file_path` always reports base_level.tscn
## and cannot be used to tell the levels apart. This id picks the background
## artwork, the tileset, the music, and the entry in the save file.
@export var level_id: String = "level_01"

## Shown on the chapter page that opens the level.
@export var level_title: String = "ออกจากหมู่บ้าน"


func level_scene_path() -> String:
	return "res://Scenes/Levels/%s.tscn" % level_id


func level_number() -> int:
	return int(level_id.trim_prefix("level_"))


func _ready() -> void:
	GameManager.player = %Player
	GameManager.on_level_entered(level_scene_path())
	var bg := get_node_or_null("LevelBackground")
	if bg and bg.has_method("apply_level"):
		bg.apply_level(level_id)
	if %Player:
		%Player.spawn_point = %Player.global_position
	AudioManager.play_music_for(level_id)
	var key := str(level_number())
	$UserInterface.show_level_page(
		Locale.chapter_label(level_number()),
		Locale.t("lv%s_title" % key),
		Locale.t("lv%s_verse" % key),
		Locale.t("level_hint"),
		level_id
	)


func _on_player_hit_enemy(enemy: Node2D = null) -> void:
	AudioManager.play("hurt")
	if enemy != null and enemy.has_method("get_touch_damage"):
		GameManager.damage(enemy.get_touch_damage())
	else:
		GameManager.damage(8)


func _on_player_hit_trap() -> void:
	AudioManager.play("hurt")
	GameManager.damage(20)
	if GameManager.player and GameManager.player.has_method("damage_tween"):
		GameManager.player.damage_tween()


func _on_fall_kill_body_entered(body: Node2D) -> void:
	if not body.is_in_group("Player"):
		return
	if GameManager.god_mode:
		body.global_position = body.spawn_point
		body.velocity = Vector2.ZERO
		return
	GameManager.death()
