extends Node
## Load every scene and resource in the project and report anything that fails.
##
## Godot's --import pass only checks asset importers, not whether a .tscn or
## .tres resolves its references, so broken node paths, missing sub-resources and
## out-of-range tileset cells stay silent until the scene is opened.
##
## This runs as a scene rather than through --script so the autoloads exist;
## otherwise every script that mentions GameManager fails to compile and buries
## the real errors.
##
## Usage: godot --headless --path . res://scripts/check_resources.tscn

const ROOTS := ["res://Scenes", "res://Assets/Generated", "res://scripts"]
const SUFFIXES := [".tscn", ".tres"]


func _ready() -> void:
	var bad := 0
	var checked := 0
	for path in _all():
		if path.ends_with("check_resources.tscn"):
			continue
		checked += 1
		if ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_IGNORE) == null:
			print("FAIL  ", path)
			bad += 1
	print("checked %d resources, %d failed" % [checked, bad])
	get_tree().quit(1 if bad > 0 else 0)


func _all() -> Array[String]:
	var found: Array[String] = []
	var queue: Array = ROOTS.duplicate()
	while not queue.is_empty():
		var dir_path: String = queue.pop_back()
		var dir := DirAccess.open(dir_path)
		if dir == null:
			continue
		for name in dir.get_directories():
			queue.append(dir_path.path_join(name))
		for name in dir.get_files():
			for suffix in SUFFIXES:
				if name.ends_with(suffix):
					found.append(dir_path.path_join(name))
	found.sort()
	return found
