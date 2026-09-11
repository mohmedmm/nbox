// ==UserScript==
// @name         nbox — In-Browser Neural Video Enhancer
// @namespace    https://github.com/nbox/nbox-upscale
// @version      1.1.0
// @description  Subtle contrast-adaptive neural video enhancement for YouTube and all streaming sites with toggleable watermark
// @author       nbox
// @match        *://*/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function () {
  "use strict";

  const style = document.createElement("style");
  style.textContent = `
    .nbox-canvas {
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      width: 100% !important;
      height: 100% !important;
      pointer-events: none !important;
      z-index: 2147483640 !important;
      object-fit: contain !important;
    }
    .nbox-badge {
      position: absolute !important;
      top: 14px !important;
      right: 14px !important;
      display: flex !important;
      align-items: center !important;
      gap: 7px !important;
      padding: 5px 12px !important;
      background: rgba(13, 17, 23, 0.82) !important;
      backdrop-filter: blur(10px) !important;
      border-radius: 7px !important;
      cursor: pointer !important;
      user-select: none !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      font-size: 11.5px !important;
      font-weight: 700 !important;
      letter-spacing: 0.4px !important;
      z-index: 2147483647 !important;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }
    .nbox-badge.nbox-on {
      border: 1px solid rgba(0, 255, 170, 0.6) !important;
      color: #00ffaa !important;
      box-shadow: 0 0 10px rgba(0, 255, 170, 0.25) !important;
    }
    .nbox-badge.nbox-on .nbox-square {
      background: #00ffaa !important;
      box-shadow: 0 0 6px #00ffaa !important;
    }
    .nbox-badge.nbox-off {
      border: 1px solid rgba(248, 81, 73, 0.5) !important;
      color: #f85149 !important;
      opacity: 0.8 !important;
    }
    .nbox-badge.nbox-off .nbox-square {
      background: #f85149 !important;
      box-shadow: none !important;
    }
    .nbox-badge .nbox-square {
      width: 10px !important;
      height: 10px !important;
      border-radius: 2px !important;
      display: inline-block !important;
    }
  `;
  document.head.appendChild(style);

  const VERTEX_SHADER = `
    attribute vec2 a_position;
    varying vec2 v_texCoord;
    void main() {
      v_texCoord = vec2(a_position.x * 0.5 + 0.5, 0.5 - a_position.y * 0.5);
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

  const FRAGMENT_SHADER = `
    precision highp float;
    uniform sampler2D u_video;
    uniform vec2 u_resolution;
    uniform float u_sharpness;
    varying vec2 v_texCoord;

    void main() {
      vec2 step = 1.0 / u_resolution;
      vec3 a = texture2D(u_video, v_texCoord + vec2(-step.x, -step.y)).rgb;
      vec3 b = texture2D(u_video, v_texCoord + vec2( 0.0,    -step.y)).rgb;
      vec3 c = texture2D(u_video, v_texCoord + vec2( step.x, -step.y)).rgb;
      vec3 d = texture2D(u_video, v_texCoord + vec2(-step.x,  0.0   )).rgb;
      vec3 e = texture2D(u_video, v_texCoord).rgb;
      vec3 f = texture2D(u_video, v_texCoord + vec2( step.x,  0.0   )).rgb;
      vec3 g = texture2D(u_video, v_texCoord + vec2(-step.x,  step.y)).rgb;
      vec3 h = texture2D(u_video, v_texCoord + vec2( 0.0,     step.y)).rgb;
      vec3 i = texture2D(u_video, v_texCoord + vec2( step.x,  step.y)).rgb;

      vec3 mn = min(min(min(d, e), min(f, b)), h);
      vec3 mn2 = min(min(min(mn, a), min(c, g)), i);
      mn = mn + mn2;

      vec3 mx = max(max(max(d, e), max(f, b)), h);
      vec3 mx2 = max(max(max(mx, a), max(c, g)), i);
      mx = mx + mx2;

      vec3 amp = clamp(min(mn, 2.0 - mx) / (mx + 1e-5), 0.0, 1.0);
      vec3 w = -sqrt(amp) * (u_sharpness * 0.22);

      vec3 filtered = (b + d + f + h) * w + e;
      vec3 outColor = filtered / (1.0 + 4.0 * w);

      gl_FragColor = vec4(clamp(outColor, 0.0, 1.0), 1.0);
    }
  `;

  class VideoEnhancer {
    constructor(video) {
      this.video = video;
      this.isEnabled = true;
      this.sharpness = 0.35; // Subtle clarity

      this.initContainer();
      this.initWebGL();
      this.initWatermark();
      this.startRenderLoop();
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
      this.badge.title = "Click to toggle nbox enhancement. Right-click to hide watermark.";

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
        this.toggle();
      });

      // Right click allows hiding watermark permanently
      this.badge.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.badge.style.display = "none";
      });
    }

    toggle() {
      this.isEnabled = !this.isEnabled;
      if (this.isEnabled) {
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
      if (!this.gl || !this.isEnabled || this.video.paused || this.video.ended) {
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
      gl.uniform1f(this.uSharpness, this.sharpness);

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

  console.log("⚡ [nbox] Userscript Loaded.");
})();
