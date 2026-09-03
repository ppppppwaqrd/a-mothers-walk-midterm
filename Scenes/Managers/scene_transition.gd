extends CanvasLayer
## Autoload. Changes scenes by turning a page over the screen.
##
## The page sweeps in to cover the old scene, the swap happens behind it, then it
## sweeps back off to reveal the new one. Call it from anywhere:
##     SceneTransition.load_scene(packed_scene)
##     SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")

const SWEEP := 0.55

var _page: ColorRect
var _busy := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_page = $Page
	_page.hide()
	_set_progress(0.0)


func load_scene(target: PackedScene) -> void:
	if target == null:
		return
	await _turn()
	get_tree().change_scene_to_packed(target)
	await _turn_back()


func load_scene_path(path: String) -> void:
	if not ResourceLoader.exists(path):
		push_warning("no scene at %s" % path)
		return
	await _turn()
	get_tree().change_scene_to_file(path)
	await _turn_back()


func _turn() -> void:
	# A second change_scene while one is mid-flight would swap the tree out from
	# under the first call and leave the page stuck over the screen.
	while _busy:
		await get_tree().process_frame
	_busy = true
	_page.show()
	AudioManager.play("page_turn")
	await _sweep(0.0, 1.0)


func _turn_back() -> void:
	# One frame for the incoming scene to lay itself out before it is revealed.
	await get_tree().process_frame
	await _sweep(1.0, 0.0)
	_page.hide()
	_busy = false


func _sweep(from: float, to: float) -> void:
	_set_progress(from)
	var tween := create_tween()
	tween.tween_method(_set_progress, from, to, SWEEP).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
	await tween.finished


func _set_progress(value: float) -> void:
	var material := _page.material as ShaderMaterial
	if material != null:
		material.set_shader_parameter("progress", value)
