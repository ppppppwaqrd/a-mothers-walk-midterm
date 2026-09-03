@tool
extends Control
## The illustration plate behind a storybook page.
##
## Every framing screen (menu, credits, game over, game win, options) wants the
## same three layers behind its paper panel: a full-bleed painting, a warm scrim
## so text stays readable over it, and the paper vignette the HUD uses. Only the
## painting differs, so the layers are built here rather than copied into five
## scene files.

@export var plate: Texture2D:
	set(value):
		plate = value
		if _art != null:
			_art.texture = value

@export var scrim: Color = Color(0.07, 0.045, 0.025, 0.36):
	set(value):
		scrim = value
		if _shade != null:
			_shade.color = value

const FRAME := "res://Assets/Generated/UI/page_frame.png"

var _art: TextureRect
var _shade: ColorRect


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	_art = TextureRect.new()
	_art.texture = plate
	_art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_add(_art)

	_shade = ColorRect.new()
	_shade.color = scrim
	_add(_shade)

	var vignette := NinePatchRect.new()
	vignette.texture = load(FRAME)
	vignette.patch_margin_left = 40
	vignette.patch_margin_top = 40
	vignette.patch_margin_right = 40
	vignette.patch_margin_bottom = 40
	_add(vignette)


func _add(child: Control) -> void:
	add_child(child)
	child.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
