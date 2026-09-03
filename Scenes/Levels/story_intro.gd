extends Node2D
## Opening pages of the book: the story, then every rule, before chapter 1.

var _index: int = 0
var _turning: bool = false


func _ready() -> void:
	AudioManager.play_music("menu_theme")
	if not Locale.language_changed.is_connected(_on_language_changed):
		Locale.language_changed.connect(_on_language_changed)
	_show_page(0, false)


func _on_language_changed() -> void:
	_show_page(_index, false)


func _unhandled_input(event: InputEvent) -> void:
	if _turning or not event.is_pressed() or event.is_echo():
		return
	if event.is_action_pressed("ui_right") or event.is_action_pressed("ui_accept") or event.is_action_pressed("Jump"):
		_on_next_pressed()
	elif event.is_action_pressed("ui_left"):
		_on_prev_pressed()
	elif event.is_action_pressed("ui_cancel"):
		_finish()


func _on_next_pressed() -> void:
	if _index >= Locale.story_pages().size() - 1:
		_finish()
		return
	_show_page(_index + 1, true)


func _on_prev_pressed() -> void:
	if _index <= 0:
		return
	_show_page(_index - 1, true)


func _on_skip_pressed() -> void:
	_finish()


func _show_page(index: int, animate: bool) -> void:
	if _turning:
		return
	var pages: Array = Locale.story_pages()
	_index = clampi(index, 0, pages.size() - 1)
	var page: Dictionary = pages[_index]
	%Chapter.text = str(page.get("chapter", ""))
	%Title.text = str(page.get("title", ""))
	%Body.text = str(page.get("body", ""))
	%Folio.text = Locale.tf("story_folio", [_index + 1, pages.size()])
	var art_path := str(page.get("art", ""))
	if art_path != "" and ResourceLoader.exists(art_path):
		%Illustration.texture = load(art_path) as Texture2D
		%Illustration.visible = true
	else:
		%Illustration.visible = false
	%btnPrev.disabled = _index <= 0
	%btnPrev.text = Locale.t("story_prev")
	%btnNext.text = Locale.t("story_begin") if _index >= pages.size() - 1 else Locale.t("story_next")
	$CanvasLayer/UI/btnSkip.text = Locale.t("story_skip")
	if animate:
		_flip()
	else:
		%Page.scale = Vector2.ONE
		%Page.modulate.a = 1.0


func _flip() -> void:
	_turning = true
	AudioManager.play("page_turn")
	%Page.pivot_offset = %Page.size * 0.5
	var tween := create_tween()
	tween.tween_property(%Page, "scale", Vector2(0.96, 0.96), 0.12)
	tween.parallel().tween_property(%Page, "modulate:a", 0.72, 0.12)
	tween.tween_property(%Page, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(%Page, "modulate:a", 1.0, 0.2)
	await tween.finished
	_turning = false


func _finish() -> void:
	if _turning:
		return
	_turning = true
	AudioManager.play("ui_click")
	SceneTransition.load_scene_path("res://Scenes/Levels/level_01.tscn")
