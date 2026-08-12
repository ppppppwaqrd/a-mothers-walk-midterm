from pathlib import Path
from collections import deque
from PIL import Image

SRC = Path(r"2D-Platformer-Starter-Kit-main/Assets/Generated/Spritesheet")


def is_bg(r, g, b, a, thr=235):
	if a < 10:
		return True
	if min(r, g, b) >= thr:
		return True
	if r >= thr - 5 and g >= thr - 15 and b >= thr - 25 and (r + g + b) / 3 >= thr - 10:
		return True
	return False


def flood_clear(im, thr=235):
	w, h = im.size
	px = im.load()
	visited = [[False] * w for _ in range(h)]
	q = deque()

	for x in range(w):
		for y in (0, h - 1):
			r, g, b, a = px[x, y]
			if is_bg(r, g, b, a, thr):
				q.append((x, y))
				visited[y][x] = True
	for y in range(h):
		for x in (0, w - 1):
			if not visited[y][x]:
				r, g, b, a = px[x, y]
				if is_bg(r, g, b, a, thr):
					q.append((x, y))
					visited[y][x] = True

	cleared = 0
	while q:
		x, y = q.popleft()
		r, g, b, a = px[x, y]
		if a != 0:
			px[x, y] = (r, g, b, 0)
			cleared += 1
		for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
			if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
				rr, gg, bb, aa = px[nx, ny]
				if is_bg(rr, gg, bb, aa, thr):
					visited[ny][nx] = True
					q.append((nx, ny))
	return cleared


def despill_and_smooth(im, passes=2):
	w, h = im.size
	for _ in range(passes):
		px = im.load()
		data = [[px[x, y] for x in range(w)] for y in range(h)]
		for y in range(h):
			for x in range(w):
				r, g, b, a = data[y][x]
				if a == 0:
					continue
				near_t = False
				for nx, ny in (
					(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
					(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1),
				):
					if 0 <= nx < w and 0 <= ny < h and data[ny][nx][3] == 0:
						near_t = True
						break
				if not near_t:
					continue

				avg = (r + g + b) / 3
				mx = max(r, g, b)
				mn = min(r, g, b)
				if avg >= 205 and (mx - mn) <= 45:
					px[x, y] = (r, g, b, 0)
					continue

				if avg >= 155:
					dark = None
					for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
						if 0 <= nx < w and 0 <= ny < h:
							rr, gg, bb, aa = data[ny][nx]
							if aa > 200 and (rr + gg + bb) / 3 < avg - 15:
								dark = (rr, gg, bb, aa)
								break
					if dark:
						t = min(1.0, (avg - 130) / 110)
						nr = int(r * (1 - t) + dark[0] * t)
						ng = int(g * (1 - t) + dark[1] * t)
						nb = int(b * (1 - t) + dark[2] * t)
						na = int(a * (1 - 0.4 * t))
						px[x, y] = (nr, ng, nb, max(0, na))
					elif avg >= 190:
						px[x, y] = (r, g, b, int(a * 0.35))


def clean_file(path: Path):
	im = Image.open(path).convert("RGBA")
	c = 0
	c += flood_clear(im, thr=238)
	c += flood_clear(im, thr=228)
	despill_and_smooth(im, passes=3)
	c += flood_clear(im, thr=218)
	despill_and_smooth(im, passes=2)
	# Drop almost-invisible pale crumbs
	px = im.load()
	w, h = im.size
	for y in range(h):
		for x in range(w):
			r, g, b, a = px[x, y]
			if 0 < a < 40 and (r + g + b) / 3 > 180:
				px[x, y] = (r, g, b, 0)
	im.save(path)
	opaque = sum(1 for p in im.getdata() if p[3] > 0)
	print(f"{path.name}: flood_cleared~{c}, opaque_left={opaque}")


def main():
	for name in [
		"mother_idle.png",
		"mother_walk.png",
		"mother_jump.png",
		"mother_throw.png",
	]:
		clean_file(SRC / name)


if __name__ == "__main__":
	main()
