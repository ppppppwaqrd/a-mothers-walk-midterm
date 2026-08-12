extends Enemy

func _ready() -> void:
	super._ready()
	var anim: AnimatedSprite2D = $Sprite/AnimateSprite
	if anim and anim.sprite_frames:
		anim.play()
