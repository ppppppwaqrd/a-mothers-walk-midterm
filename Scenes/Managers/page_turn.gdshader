shader_type canvas_item;

// A leaf of paper sweeping across the screen, for changing scenes.
//
// `progress` runs 0 (screen clear) to 1 (screen covered). The leading edge bows
// the way a real page does when it lifts, carries a highlight along the fold and
// throws a soft shadow onto whatever is still visible ahead of it.

uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform vec4 paper_color : source_color = vec4(0.945, 0.914, 0.831, 1.0);
uniform vec4 shadow_color : source_color = vec4(0.13, 0.09, 0.06, 1.0);
// How wide the lifted part of the page is, as a fraction of the screen.
uniform float curl : hint_range(0.02, 0.4) = 0.13;
uniform float grain_strength : hint_range(0.0, 0.2) = 0.05;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(41.317, 289.113))) * 43758.5453);
}

float grain(vec2 uv) {
	vec2 p = uv * 420.0;
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash(i);
	float b = hash(i + vec2(1.0, 0.0));
	float c = hash(i + vec2(0.0, 1.0));
	float d = hash(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void fragment() {
	// The page enters from the right, so it starts fully off-screen at curl+1.
	float bow = curl * 0.42 * sin(UV.y * PI);
	float edge = mix(1.0 + curl, -curl, progress) + bow;
	float d = UV.x - edge;

	float cover = smoothstep(-0.003, 0.003, d);
	float lift = 1.0 - clamp(d / curl, 0.0, 1.0);
	float shade = 1.0 + 0.26 * lift - 0.62 * pow(lift, 7.0);

	vec3 paper = paper_color.rgb * shade;
	paper *= 1.0 - grain_strength + grain_strength * 2.0 * grain(UV);

	// Cast ahead of the fold, fading fast, so the page reads as lifted off.
	float cast_shadow = (1.0 - cover) * 0.55 * exp(max(0.0, -d) * -22.0);

	COLOR = vec4(mix(shadow_color.rgb, paper, cover), max(cover, cast_shadow));
}
