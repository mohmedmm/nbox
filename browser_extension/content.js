/**
 * nbox — In-Browser Subtle Neural Video Enhancer
 * Universal contrast-adaptive clarity engine for YouTube, Twitch, and all video sites.
 */

(function () {
  "use strict";

  const VERTEX_SHADER = `
    attribute vec2 a_position;
    varying vec2 v_texCoord;
    void main() {
      v_texCoord = vec2(a_position.x * 0.5 + 0.5, 0.5 - a_position.y * 0.5);
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

  // Contrast-Adaptive Sharpening (CAS) GLSL Shader — Subtle & Natural Clarity
  const FRAGMENT_SHADER = `
    precision highp float;
    uniform sampler2D u_video;
    uniform vec2 u_resolution;
    uniform float u_sharpness;
    varying vec2 v_texCoord;

    void main() {
      vec2 step = 1.0 / u_resolution;

      // Sample 3x3 cross neighborhood
      vec3 a = texture2D(u_video, v_texCoord + vec2(-step.x, -step.y)).rgb;
      vec3 b = texture2D(u_video, v_texCoord + vec2( 0.0,    -step.y)).rgb;
      vec3 c = texture2D(u_video, v_texCoord + vec2( step.x, -step.y)).rgb;
      vec3 d = texture2D(u_video, v_texCoord + vec2(-step.x,  0.0   )).rgb;
      vec3 e = texture2D(u_video, v_texCoord).rgb;
      vec3 f = texture2D(u_video, v_texCoord + vec2( step.x,  0.0   )).rgb;
      vec3 g = texture2D(u_video, v_texCoord + vec2(-step.x,  step.y)).rgb;
      vec3 h = texture2D(u_video, v_texCoord + vec2( 0.0,     step.y)).rgb;
      vec3 i = texture2D(u_video, v_texCoord + vec2( step.x,  step.y)).rgb;

      // Local min and max bounds for halo suppression
      vec3 mn = min(min(min(d, e), min(f, b)), h);
      vec3 mn2 = min(min(min(mn, a), min(c, g)), i);
      mn = mn + mn2;

      vec3 mx = max(max(max(d, e), max(f, b)), h);
      vec3 mx2 = max(max(max(mx, a), max(c, g)), i);
      mx = mx + mx2;

      // Smooth contrast calculation
      vec3 amp = clamp(min(mn, 2.0 - mx) / (mx + 1e-5), 0.0, 1.0);
      vec3 w = -sqrt(amp) * (u_sharpness * 0.22);

      // Filtered output
      vec3 filtered = (b + d + f + h) * w + e;
      vec3 outColor = filtered / (1.0 + 4.0 * w);

      gl_FragColor = vec4(clamp(outColor, 0.0, 1.0), 1.0);
    }
  `;

  let globalSettings = {
    enabled: true,
    showWatermark: true,
    sharpness: 0.35,
  };

  // Sync settings from storage
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(
      { nboxEnabled: true, nboxShowWatermark: true, nboxSharpness: 35 },
      (items) => {
        globalSettings.enabled = items.nboxEnabled;
        globalSettings.showWatermark = items.nboxShowWatermark;
        globalSettings.sharpness = items.nboxSharpness / 100.0;
        updateAllEnhancers();
      }
    );

    chrome.storage.onChanged.addListener((changes) => {
      if (changes.nboxEnabled) globalSettings.enabled = changes.nboxEnabled.newValue;
      if (changes.nboxShowWatermark) globalSettings.showWatermark = changes.nboxShowWatermark.newValue;
      if (changes.nboxSharpness) globalSettings.sharpness = changes.nboxSharpness.newValue / 100.0;
      updateAllEnhancers();
    });
  }

  const activeEnhancers = new Set();

  function updateAllEnhancers() {
    activeEnhancers.forEach((enhancer) => enhancer.applySettings());
  }

  class VideoEnhancer {
    constructor(video) {
      this.video = video;
      this.initContainer();
      this.initWebGL();
      this.initWatermark();
      this.applySettings();
      this.startRenderLoop();
      activeEnhancers.add(this);
    }

    initContainer() {
      this.container =
        this.video.closest(".html5-video-player") ||
        this.video.closest("#movie_player") ||
        this.video.parentElement;

      if (getComputedStyle(this.container).position === "static") {
        this.container.style.position = "relative";
      }
    }

    initWebGL() {
      this.canvas = document.createElement("canvas");
      this.canvas.className = "nbox-canvas";
      this.container.appendChild(this.canvas);

      const gl =
        this.canvas.getContext("webgl2") || this.canvas.getContext("webgl");
      if (!gl) return;
      this.gl = gl;

      const vs = this.createShader(gl.VERTEX_SHADER, VERTEX_SHADER);
      const fs = this.createShader(gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
      const program = gl.createProgram();
      gl.attachShader(program, vs);
      gl.attachShader(program, fs);
      gl.linkProgram(program);
      gl.useProgram(program);
      this.program = program;

      const posBuffer = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
        gl.STATIC_DRAW
      );

      const aPos = gl.getAttribLocation(program, "a_position");
      gl.enableVertexAttribArray(aPos);
      gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

      this.texture = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, this.texture);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

      this.uResolution = gl.getUniformLocation(program, "u_resolution");
      this.uSharpness = gl.getUniformLocation(program, "u_sharpness");
    }

    createShader(type, src) {
      const s = this.gl.createShader(type);
      this.gl.shaderSource(s, src);
      this.gl.compileShader(s);
      return s;
    }

    initWatermark() {
      this.badge = document.createElement("div");
      this.badge.className = "nbox-badge nbox-on";
      this.badge.title = "Click to toggle nbox Neural Video Enhancement";

      this.square = document.createElement("span");
      this.square.className = "nbox-square";

      this.text = document.createElement("span");
      this.text.className = "nbox-text";
      this.text.textContent = "nbox: ON";

      this.badge.appendChild(this.square);
      this.badge.appendChild(this.text);
      this.container.appendChild(this.badge);

      this.badge.addEventListener("click", (e) => {
        e.stopPropagation();
        globalSettings.enabled = !globalSettings.enabled;
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
          chrome.storage.local.set({ nboxEnabled: globalSettings.enabled });
        }
        updateAllEnhancers();
      });
    }

    applySettings() {
      if (!this.badge || !this.canvas) return;

      // Handle Watermark Visibility Toggle
      if (globalSettings.showWatermark) {
        this.badge.style.display = "flex";
      } else {
        this.badge.style.display = "none";
      }

      // Handle Enabled / Disabled State
      if (globalSettings.enabled) {
        this.badge.className = "nbox-badge nbox-on";
        this.text.textContent = "nbox: ON";
        this.canvas.style.display = "block";
      } else {
        this.badge.className = "nbox-badge nbox-off";
        this.text.textContent = "nbox: OFF";
        this.canvas.style.display = "none";
      }
    }

    renderFrame() {
      if (!this.gl || !globalSettings.enabled || this.video.paused || this.video.ended) {
        return;
      }

      const vw = this.video.videoWidth;
      const vh = this.video.videoHeight;
      if (!vw || !vh) return;

      const cw = this.video.clientWidth || vw;
      const ch = this.video.clientHeight || vh;

      if (this.canvas.width !== cw || this.canvas.height !== ch) {
        this.canvas.width = cw;
        this.canvas.height = ch;
        this.gl.viewport(0, 0, cw, ch);
      }

      const gl = this.gl;
      gl.bindTexture(gl.TEXTURE_2D, this.texture);
      gl.texImage2D(
        gl.TEXTURE_2D,
        0,
        gl.RGBA,
        gl.RGBA,
        gl.UNSIGNED_BYTE,
        this.video
      );

      gl.uniform2f(this.uResolution, cw, ch);
      gl.uniform1f(this.uSharpness, globalSettings.sharpness);

      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }

    startRenderLoop() {
      const loop = () => {
        this.renderFrame();
        if ("requestVideoFrameCallback" in this.video) {
          this.video.requestVideoFrameCallback(loop);
        } else {
          requestAnimationFrame(loop);
        }
      };

      if ("requestVideoFrameCallback" in this.video) {
        this.video.requestVideoFrameCallback(loop);
      } else {
        requestAnimationFrame(loop);
      }
    }
  }

  const attachedVideos = new WeakSet();

  function scanForVideos() {
    const videos = document.querySelectorAll("video");
    videos.forEach((v) => {
      if (!attachedVideos.has(v) && v.videoWidth > 0) {
        attachedVideos.add(v);
        new VideoEnhancer(v);
      } else if (!attachedVideos.has(v)) {
        v.addEventListener(
          "loadedmetadata",
          () => {
            if (!attachedVideos.has(v)) {
              attachedVideos.add(v);
              new VideoEnhancer(v);
            }
          },
          { once: true }
        );
      }
    });
  }

  scanForVideos();

  const observer = new MutationObserver(() => scanForVideos());
  observer.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });

  console.log("⚡ [nbox] Subtle Neural Video Enhancer Active.");
})();
