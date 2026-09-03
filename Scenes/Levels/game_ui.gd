extends CanvasLayer
## The in-level HUD: status panel, tool buttons, touch pad, and the pages that
## open over the top of them (chapter title, pause).

## Below this the patience bar pulses and the warning sound plays, once.
const PATIENCE_WARNING := 25.0

## How fast the bars chase their real value, in units per second. Slow enough
## to see the hit land, fast enough that the number is never misleading.
const BAR_CHASE := 90.0

@onready var _hearts: Array[Node] = %Lives.get_children()

var _patience_warned := false
var _heartbeat: Tween
var _shown_kratib := -1
var _shown_life := -1


func _ready() -> void:
	%LevelPage.dismissed.connect(_on_level_page_dismissed)
	# The touch pad only earns its screen space on a device without a keyboard.
	%TouchPad.visible = DisplayServer.is_touchscreen_available()
	GameManager.god_mode_changed.connect(_on_god_mode_changed)
	_on_god_mode_changed(GameManager.god_mode)


func _on_god_mode_changed(on: bool) -> void:
	if has_node("%GodBadge"):
		%GodBadge.visible = on
	if on:
		alert("โหมดทดลอง — F10 ปิด")


func _process(delta: float) -> void:
	%AmmoLabel.text = "x%d" % GameManager.ammo
	%HpBar.max_value = GameManager.max_hp
	%PatienceBar.max_value = GameManager.max_patience
	# Slide rather than snap, so a chunk of damage is visible after the fact.
	%HpBar.value = move_toward(%HpBar.value, GameManager.hp, BAR_CHASE * delta)
	%PatienceBar.value = move_toward(%PatienceBar.value, GameManager.patience, BAR_CHASE * delta)
	%btnMusic.icon = preload("res://Assets/Generated/UI/icon_music_on.png") if GameManager.music_on else preload("res://Assets/Generated/UI/icon_music_off.png")
	%btnSound.icon = preload("res://Assets/Generated/UI/icon_sound_on.png") if GameManager.sfx_on else preload("res://Assets/Generated/UI/icon_sound_off.png")
	%btnMusic.modulate.a = 1.0 if GameManager.music_on else 0.7
	%btnSound.modulate.a = 1.0 if GameManager.sfx_on else 0.7
	_update_score()
	_update_hearts()
	_update_patience_warning()


## Bump the count when it changes, so a basket picked up off screen still reads.
func _update_score() -> void:
	if GameManager.kratib == _shown_kratib:
		return
	_shown_kratib = GameManager.kratib
	%ScoreLabel.text = "%d/%d" % [_shown_kratib, GameManager.kratib_needed]
	%ScoreLabel.pivot_offset = %ScoreLabel.size * 0.5
	var tween := create_tween()
	tween.tween_property(%ScoreLabel, "scale", Vector2(1.35, 1.35), 0.09)
	tween.tween_property(%ScoreLabel, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)


## Hearts stay on the page; spent ones fade to the empty drawing.
func _update_hearts() -> void:
	if GameManager.life == _shown_life:
		return
	var gained: bool = GameManager.life > _shown_life
	var old_life := _shown_life
	_shown_life = GameManager.life
	var full := preload("res://Assets/Generated/UI/icon_heart_full.png")
	var empty := preload("res://Assets/Generated/UI/icon_heart_empty.png")
	for i in _hearts.size():
		var heart: TextureRect = _hearts[i]
		var want: bool = i < _shown_life
		var was_full: bool = old_life >= 0 and i < old_life
		heart.visible = true
		heart.texture = full if want else empty
		heart.modulate.a = 1.0 if want else 0.55
		if want == was_full:
			continue
		heart.pivot_offset = heart.size * 0.5
		var tween := create_tween()
		if want:
			heart.scale = Vector2.ZERO
			tween.tween_property(heart, "scale", Vector2.ONE, 0.26).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
		else:
			tween.tween_property(heart, "scale", Vector2(1.25, 1.25), 0.08)
			tween.tween_property(heart, "scale", Vector2.ONE, 0.18)
	if old_life >= 0 and not gained:
		_shake_status()


## A short jolt of the whole status panel: the cheapest way to sell a life lost.
func _shake_status() -> void:
	var panel: Control = %Lives.get_parent()
	var home: Vector2 = panel.position
	var tween := create_tween()
	for i in 4:
		var amount: float = 7.0 * (1.0 - i / 4.0)
		tween.tween_property(panel, "position", home + Vector2(amount, -amount * 0.4), 0.04)
		tween.tween_property(panel, "position", home - Vector2(amount, -amount * 0.4), 0.04)
	tween.tween_property(panel, "position", home, 0.04)


func open_minigame(game_id: String, hard: bool = false) -> void:
	if not has_node("%MinigameHost"):
		return
	if not %MinigameHost.finished.is_connected(_on_minigame_finished):
		%MinigameHost.finished.connect(_on_minigame_finished)
	%MinigameHost.open(game_id, hard)


func _on_minigame_finished(won: bool) -> void:
	if won:
		alert("ได้ความอดทน +20 และก้อนหิน +3")
	else:
		alert("เทวดาไม่พอใจ — ไอ้ทองรอไม่ไหวเร็วขึ้น")


func _unhandled_input(event: InputEvent) -> void:
	if has_node("%MinigameHost") and %MinigameHost.visible:
		return
	if event.is_action_pressed("Pause"):
		%PauseMenu.toggle()
		get_viewport().set_input_as_handled()


## Open the chapter page for a level. The level stays paused behind it.
func show_level_page(chapter: String, title: String, hint: String, level_id: String = "") -> void:
	get_tree().paused = true
	%LevelPage.open(chapter, title, hint, level_id)


func _on_level_page_dismissed() -> void:
	get_tree().paused = false


## A paper strip that slides in, holds, and leaves. Used for pickups and hints.
func alert(text: String) -> void:
	%Message.text = text
	%Toast.show()
	%Toast.modulate.a = 0.0
	%Toast.scale = Vector2(0.9, 0.9)
	var tween := create_tween().set_parallel(true)
	tween.tween_property(%Toast, "modulate:a", 1.0, 0.18)
	tween.tween_property(%Toast, "scale", Vector2.ONE, 0.24).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	await get_tree().create_timer(2.2).timeout
	if not is_instance_valid(self):
		return
	var out := create_tween()
	out.tween_property(%Toast, "modulate:a", 0.0, 0.25)
	await out.finished
	%Toast.hide()


## Pulse the bar and sound the warning once, when Ai Tong is nearly out of time.
func _update_patience_warning() -> void:
	var low: bool = GameManager.patience <= PATIENCE_WARNING and GameManager.patience > 0.0
	if low == (_heartbeat != null and _heartbeat.is_valid()):
		return
	if low:
		if not _patience_warned:
			_patience_warned = true
			AudioManager.play("patience_low")
		_heartbeat = create_tween().set_loops()
		_heartbeat.tween_property(%PatienceBar, "modulate", Color(1.0, 0.55, 0.45), 0.4)
		_heartbeat.tween_property(%PatienceBar, "modulate", Color.WHITE, 0.4)
	else:
		if _heartbeat != null and _heartbeat.is_valid():
			_heartbeat.kill()
		_heartbeat = null
		%PatienceBar.modulate = Color.WHITE
		_patience_warned = false


func _on_btn_sound_pressed() -> void:
	GameManager.sfx_on = not GameManager.sfx_on
	GameManager.update_option()
	GameManager.save_option()
	AudioManager.play("ui_click")


func _on_btn_music_pressed() -> void:
	GameManager.music_on = not GameManager.music_on
	GameManager.update_option()
	GameManager.save_option()
	AudioManager.play("ui_click")


func _on_btn_save_pressed() -> void:
	GameManager.save_game()
	AudioManager.play("ui_click")
	alert("คัดลอกหน้านี้ไว้แล้ว")


func _on_btn_pause_pressed() -> void:
	%PauseMenu.toggle()


func _on_btn_left_pressed() -> void:
	Input.action_press("Left")


func _on_btn_left_released() -> void:
	Input.action_release("Left")


func _on_btn_up_pressed() -> void:
	Input.action_press("Jump")


func _on_btn_up_released() -> void:
	Input.action_release("Jump")


func _on_btn_right_pressed() -> void:
	Input.action_press("Right")


func _on_btn_right_released() -> void:
	Input.action_release("Right")


func _on_btn_shoot_button_down() -> void:
	Input.action_press("Shoot")


func _on_btn_shoot_button_up() -> void:
	Input.action_release("Shoot")
