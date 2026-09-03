extends Node2D
## Credits page: a paper leaf that opens, then the names settle in like ink.

func _ready() -> void:
	AudioManager.play_music("menu_theme")
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)
	_play_intro()


func _apply_locale() -> void:
	%Title.text = Locale.t("credit_title")
	%Group.text = Locale.t("credit_group")
	%Course.text = Locale.t("credit_course")
	%Craft.text = Locale.t("credit_craft")
	%Colophon.text = Locale.t("credit_colophon")
	$CanvasLayer/UI/btnBack.text = Locale.t("opt_back")


func _play_intro() -> void:
	%Page.pivot_offset = %Page.size * 0.5
	%Page.rotation_degrees = -2.2
	%Page.scale = Vector2(0.92, 0.92)
	%Page.modulate.a = 0.0
	for node in [%Title, %Rule, %Members, %Group, %Course, %Craft, %Colophon]:
		node.modulate.a = 0.0
	var intro := create_tween()
	intro.set_parallel(true)
	intro.tween_property(%Page, "modulate:a", 1.0, 0.4)
	intro.tween_property(%Page, "scale", Vector2.ONE, 0.55).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	intro.tween_property(%Page, "rotation_degrees", 0.0, 0.55)
	await intro.finished
	AudioManager.play("page_turn")
	await _fade_in(%Title, 0.32)
	await _fade_in(%Rule, 0.18)
	await _fade_in(%Members, 0.42)
	await _fade_in(%Group, 0.28)
	await _fade_in(%Course, 0.28)
	await _fade_in(%Craft, 0.32)
	await _fade_in(%Colophon, 0.36)
	_idle_sway()


func _fade_in(node: CanvasItem, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(node, "modulate:a", 1.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await tween.finished


func _idle_sway() -> void:
	var sway := create_tween().set_loops()
	sway.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	sway.tween_property(%Page, "rotation_degrees", 0.55, 2.6)
	sway.tween_property(%Page, "rotation_degrees", -0.55, 2.6)


func _on_btn_back_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
