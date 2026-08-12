extends Enemy
## Crow patrols in the air (no floor needed).

@export var patrol_width: float = 220.0

var _origin_x: float = 0.0


func _ready() -> void:
	super._ready()
	_origin_x = global_position.x
	# Soft collision so crow doesn't get stuck on platforms as easily
	collision_mask = 1


func _physics_process(_delta: float) -> void:
	if not alive:
		return
	velocity.y = 0.0
	if absf(global_position.x - _origin_x) > patrol_width * 0.5:
		direction = -1 if global_position.x > _origin_x else 1
		_update_facing()
	elif is_on_wall() or wall_ray.is_colliding():
		direction = -direction
		_update_facing()
	velocity.x = speed * direction
	move_and_slide()
