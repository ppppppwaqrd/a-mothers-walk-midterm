extends StaticBody2D

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D


func _ready() -> void:
	collision.disabled = true
	_loop()


func _loop() -> void:
	while is_inside_tree():
		await get_tree().create_timer(randf_range(0.8, 2.2)).timeout
		# retract
		sprite.frame = 0
		collision.disabled = true
		await get_tree().create_timer(0.6).timeout
		# thrust
		var frames: int = maxi(1, sprite.hframes - 1)
		for i in range(frames + 1):
			sprite.frame = i
			collision.disabled = i < int(frames * 0.35)
			await get_tree().create_timer(0.06).timeout
		await get_tree().create_timer(0.4).timeout
